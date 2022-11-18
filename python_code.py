__author__ = "Javid Jooshesh, j.jooshesh@hva.nl"
__version__ = "v1"

import ghpythonlib.treehelpers as th
import rhinoscriptsyntax as rs
import Grasshopper.Kernel.Data as ghp
import Grasshopper.Kernel.Geometry.Plane as gh_plane


class Blocks:
    """_Class representing the wood plank geometries from the database_
    Attributes:
        source (DataTree[Breps]) : The list of box breps as a Grasshopper
            datatree
    Methods:
        explode_polysrf: ...
        explode_srf: ...
        get_block_length: ...
        get_block_width: ...
    """

    def __init__(self, source):
        """_Constructor of the class_
        Args:
            source (DataTree[objectid]) : The list of box breps
                as a Grasshopper datatree
        """

        self.source = source

    def __str__(self):
        return "A Class to Represent the Functions of " \
               "Form-Fitting for the Circular Wood Blocks from Scanned Database"

    def explode_polysrf(self):
        """Explode a brep object into the NURBS untrimmed surfaces"""
        p = []
        for i in range(len(self.source)):
            trimmed_srf = rs.ExplodePolysurfaces(self.source[i])
            blocks = []
            for srf in trimmed_srf:
                blocks.append(srf)
            p.append(blocks)
        data = th.list_to_tree(p, source=[0])
        return data

    def explode_srf(self):
        """Explode the surface into line segments"""
        p = []
        listed_tree = th.tree_to_list(self.explode_polysrf())
        curve = None
        for i in range(len(listed_tree)):
            curve_segments = []
            for j in range(len(listed_tree[i])):
                curve = rs.DuplicateEdgeCurves(listed_tree[i][j])
                curve_segments.append(curve)
            p.append(curve_segments)
        data = th.list_to_tree(p, source=[0])
        return data

    def get_block_length(self, position=2):
        """Return the length of the block as float. BigO(n^2)
            (not the most efficient way but it works for now)
        """
        list_of_lengths = []
        curves = th.tree_to_list(self.explode_srf())
        for i in range(len(curves)):
            blocks = []
            for j in range(len(curves[i])):
                lengths = []
                for k in range(len(curves[i][j])):
                    l = rs.CurveLength(curves[i][j][k])
                    lengths.append(l)
            blocks.append(sorted(lengths)[position])
            list_of_lengths.append(blocks)

        lengths_data_tree = th.list_to_tree(list_of_lengths, source=[0])
        return lengths_data_tree

    def get_block_width(self, position=1):
        """Return the width of the block as float"""
        widths = self.get_block_length(position=position)
        return widths
        
    def get_block_height(self, position=3):
        heights = self.get_block_length(position=position)
        return heights


class DesignModel:
    """_Class representing the design object and methods to fit the wood planks
    that are varaible in dimensions, within the boundary of the design_

    Attributes:
        design_region (DesignRegion) : The boundary of design
        blocks (Blocks) : The box breps representing the wood planks from the
            database
    Methods:
        orient: ...
        fit_blocks: ...
    """

    def __init__(self, design_region, blocks, heights):
        """_Constructor method_"""

        self.region = DesignRegion(design_region, 0)
        self.blocks = Blocks(blocks)
        self.blocks_list = self.blocks.source
        self.design_region_brep = design_region
        self.blocks_brep = blocks
        self.blocks_length = self.blocks.get_block_length()
        self.blocks_width = self.blocks.get_block_width()
        self.blocks_height = heights

        self.index_list = []
        self.edge = self.region.find_edge(1)
        self.selection = []
        self.flatten_values()
    
    def flatten_values(self):
        """_Flatten the Length, Width and Height values_"""
        
        flatten_path_width = ghp.GH_Path(0)
        self.blocks_width.Flatten(flatten_path_width)
        flatten_path_length = ghp.GH_Path(0)
        self.blocks_length.Flatten(flatten_path_length)
        flatten_path_height = ghp.GH_Path(0)
        self.blocks_length.Flatten(flatten_path_height)

    def orient(self, index_list, positions):
        """_Orient the block across the selected edge_

        Args:
            index_list (list) : The list of indexes of elements to orient
        Returns:
            oriented (list) : The list of oriented elements
        """

        block_edges = [
            th.tree_to_list(self.blocks.explode_srf())[i][3][0] for i in range(
                len(self.blocks.source)
            )
        ]

        st_points_orient_blocks = [
            [rs.CurvePoints(edge) for edge in block_edges][i][1] for i in range(
                len(block_edges)
            )
        ]

        end_points_orient_blocks = [
            [rs.CurvePoints(edge) for edge in block_edges][i][0] for i in range(
                len(block_edges)
            )
        ]

        z_points_blocks = [
            rs.MoveObject(rs.CopyObject(point), [0, 0, 1]) for point in st_points_orient_blocks
        ]

        st_pt_edge = None

        oriented = []
        for i in range(len(positions)):
            st_pt_edge = positions[i]
            
            end_pt_edge = rs.CurvePoints(self.edge)[0]
            z_points_boundary = rs.MoveObject(rs.CopyObject(st_pt_edge), [0, 0, 1])
            j = index_list[i]
            oriented.append(
                rs.OrientObject(self.blocks.source[j],
                                [end_points_orient_blocks[j], st_points_orient_blocks[j], z_points_blocks[j]],
                                [st_pt_edge, end_pt_edge, z_points_boundary]
                                )
            )
        return oriented

    def fit_blocks(self, available_length, available_width, available_height):
        """_Create a sublist of what is suitable for populating in the boundary
        of the design. For now the criteria can be the top widths that the addition of them
        would be less than the available length of the edge_
        """
        
        evaluated_points = []
        blocks_dicts = {}
        
        widths = th.tree_to_list(self.blocks_width)  # Python list
        lengths = th.tree_to_list(self.blocks_length) # Python list
        
        target_edge = self.region.find_edge(1)
        
        for i in range(len(self.blocks.source)):
            wlh = (widths[i], lengths[i], heights[i])
            blocks_dicts[wlh] = self.blocks.source[i]

        constant_length = available_length
        initial_pos = 0.0

        for wlh, block in blocks_dicts.items():
            width = wlh[0]
            length = wlh[1]
            height = wlh[2]
            
            if (
                width <= available_length
                and length <= available_width
                and height <= available_height
            ):
                self.selection.append(block)
                remaining = width / constant_length
                
                parameter = rs.CurveParameter(target_edge, remaining)
                points_on_curve = rs.EvaluateCurve(target_edge, parameter)
                
                point_a = rs.CurvePoints(self.edge)[0]
                point_b = rs.CurvePoints(self.edge)[1]
                
                vector_3d = rs.VectorCreate(point_a, point_b)
                v = rs.VectorUnitize(vector_3d)
                scaled_vector = rs.VectorScale(v, initial_pos)
                rs.MoveObject(points_on_curve, scaled_vector)
                evaluated_points.append(points_on_curve)
                initial_pos -= width

                del blocks_dicts[wlh]
                for index, item in enumerate(self.blocks.source):
                    if item == block:
                        self.index_list.append(index)
                available_length -= width
        
        self.orient(self.index_list, evaluated_points)

        return evaluated_points
        

class DesignRegion:
    def __init__(self, brep, index):
        self.brep = brep
        self.index = index

    def explode(self):
        return rs.ExplodePolysurfaces(self.brep)

    def select_lowest_face(self):
        """Sort the faces of the Brep according to lowest `z` value of the
            centroids
        """
        exploded_surfaces = self.explode()
        z_coords = list()
        lowest_srf = None
        for i in range(len(exploded_surfaces)):
            centriod = rs.SurfaceAreaCentroid(exploded_surfaces[i])
            z_values = centriod[0][2]
            z_coords.append(z_values)
            if z_values == min(z_coords):
                lowest_srf = exploded_surfaces[i]
        return lowest_srf

    def find_edge(self, edge_index):
        """Get the edge to populate blocks across within the design boundary"""
        selected_face = self.select_lowest_face()
        for index, item in enumerate(rs.DuplicateEdgeCurves(selected_face)):
            if index == edge_index:
                return item


if __name__ == "__main__":
    objects = Blocks(wood_from_db)
    des_boundary = DesignRegion(design_boundary, 0)
    edge = des_boundary.find_edge(edge_index)
    edge_2 = des_boundary.find_edge(0)
    edge_3 = des_boundary.find_edge(1)
    length = rs.CurveLength(edge)
    width = rs.CurveLength(edge_2)
    
    test = DesignModel(design_boundary, wood_from_db, heights)
    t = th.list_to_tree(objects.source, source=[0])

    c = t.Branches[0]
    
    evaluated_points = test.fit_blocks(length, width, height)
    all_blocks = test.blocks.source
    print(test.index_list)
    indecies = test.index_list
    selected = test.selection