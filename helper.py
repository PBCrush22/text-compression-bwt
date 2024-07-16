# Beh Hanyu
# 33607265

# This file contains the helper functions and class to build Suffix Tree using Ukkonen's algorithm used in q2_encoder.py, q2_decoder.py

from bitarray import bitarray

# convert char to ascii
def char_to_ascii(char):
    return ord(char) - 36

# convert ascii to char
def ascii_to_char(ascii):
    return chr(ascii + 36)
    
# get bitarray of decimal number
def decimal_to_binary(dec):
    return bitarray(format(dec, 'b'))

# get decimal from bitarray
def binary_to_decimal(bit_array):
    # convert bitarray to binary string
    binary_string = bit_array.to01()
    
    # convert the binary string to a decimal integer
    decimal_value = int(binary_string, 2)
    
    return decimal_value

# convert char to bitarray
def char_to_binary(char):
    return bitarray('{0:07b}'.format(ord(char)))

### IMPLICIT SUFFIX TREE USING UKKONEN'S ALGORITHM ### (same code as in q1/q1.py)
# Node class is mainly use to store list of Edge objects it has and suffix link, other attributes are used for easy recognition of the node
class Node:
    def __init__(self, from_edge, start_index):
        # edge that lead to this node
        self.from_edge = from_edge
        # the smallest start index of the children edges
        self.start_index = start_index
        # list of Edge objects that the node has, only accept ascii character range of [36, 126]
        self.children_edge = [None]*91
        # suffix link of the node
        self.suffix_link = None

# create a global endpointer variable
endpointer = None

# Edge class holds all the important information of an edge in the suffix tree
class Edge:
    def __init__(self, from_node, start, j, end=None):
        # node that the edge is coming from
        self.from_node = from_node
        # TRICK 1: space-efficient representation of edge-labels/substrings
        # start index of the edge
        self.start = start
        # end index of the edge. If not provided, this value will be retrieve from the global variable endpointer when called
        self._end = end
        # node that the edge is going to, use this to do dfs traversal
        self.to_node = None
        # end index of the edge, use to construct suffix array
        self.end_index = j
        
    # TRICK 4: rapid leaf extension trick. Since a leaf is always a leaf, use global variable to keep track of the endpointer and only retrieve it when needed
    # property to get the end index of the edge based on the global variable endpointer
    @property
    def end(self):
        if self._end is None:
            return endpointer
        else:
            return self._end

    # setter to set the end index of the edge based on the global variable endpointer
    @end.setter
    def end(self, value):
        if self._end is None:
            self._end = value

# To construct the implicit suffix tree using Ukkonen's algorithm
class SuffixTree:
    def __init__(self, string):
        self.string = string
        # initialise root node and set its suffix link
        self.root = Node(None, -1)
        self.root.suffix_link = self.root
        # previous node to keep track of the new internal node created in the same phase
        self.prev_node = None
        # skipcountpointer to keep track of the successive characters along the edge
        self.skipcountpointer = None
        # set active points
        self.active_node = self.root
        self.active_edge = -1
        self.active_length = 0
        # remaining suffix count to be added to the tree in the current phase
        self.remainder = 0
        # suffix array to be constructed
        self.suffix_array = []
        
        # extend the suffix tree
        self.extend()

        # do a dfs traversal to construct the suffix array
        self.dfs(self.root)

    def extend(self):
        # Begin phase
        for i in range(len(self.string)):
            # RULE 1: Update endpointer in every phase for every leaves automatically
            global endpointer
            endpointer = i
            # remaining suffix count to be added to the tree in the current phase
            self.remainder += 1
            
            # Loop until all remaining suffixes are added to the tree
            while self.remainder > 0:
                # Begin suffix extension

                # If no active edge, set active edge to the current character
                if self.active_length == 0:
                    self.active_edge = i

                # find edge that starts with the current character
                char_index = ord(self.string[self.active_edge]) - 36
                edge = self.active_node.children_edge[char_index]

                # If edge already in the current node
                if edge:
                    # Check the boundary of the edge
                    boundary = edge.end - edge.start + 1
                    
                    # If the remainder is within the boundary
                    if boundary > self.active_length:
                        # TRICK 2: Skip/Count trick
                        # Initialise skipcountpointer to skip over successive characters along the edge
                        self.skipcountpointer = edge.start + self.active_length
                        # If there are new internal node created in the same phase, link it to the active node
                        if self.prev_node is not None:
                            self.prev_node.suffix_link = self.active_node
                        # Rule 3: current character is already in the tree, do nothing
                        if self.string[i] == self.string[self.skipcountpointer]:
                            self.active_length += 1
                            # Current phase ends, set prev_node to None
                            self.prev_node = None
                            # TRICK 3: Showstopper trick, since rule 3 require no further extension, stop prematurely
                            break
                        
                        # If the current character is not the same as the character along the edge
                        # RULE 2: Create new branch
                        # new internal node created
                        new_node = Node(None, self.skipcountpointer)
                        if self.prev_node is not None:
                            self.prev_node.suffix_link = new_node
                        # new internal edge created, which connects to the new node
                        new_internal_edge = Edge(self.active_node, edge.start, None, self.skipcountpointer - 1)
                        new_internal_edge.to_node = new_node
                        # every nodes created has suffix link to the root
                        new_node.suffix_link = self.root
                        # new edge coming out from the new internal node
                        # the end index is set to i - self.remainder + 1, which means the index of the string this edge starts from
                        new_branch_edge = Edge(new_node, i, i - self.remainder + 1)
                        # remove the previous edge connected from the active node, add new internal edge as children edge
                        self.active_node.children_edge[ord(self.string[edge.start]) - 36] = None
                        self.active_node.children_edge[ord(self.string[new_internal_edge.start]) - 36] = new_internal_edge
                        # the start point of the previous edge is updated so that its start index continue from the new internal edge end point
                        # this approach remain it as a leaf (once a leaf, always a leaf), so the info of it as a leaf (particularly the end_index) is kept
                        edge.start = self.skipcountpointer
                        # the new node points to the previous edge (which start point is updated) and the new branch edge
                        new_node.children_edge[ord(self.string[i]) - 36] = new_branch_edge
                        new_node.children_edge[ord(self.string[edge.start]) - 36] = edge
                        # set new node to prev_node for suffix link creation in later extension
                        self.prev_node = new_node
                        # if active node is root, no suffix link to travel to, just update active edge and active length so it points to the next character
                        if self.active_node is self.root:
                            if self.active_length >= 1:
                                self.active_edge = i - self.remainder + 2
                            self.active_length = max(self.active_length-1, 0)
                    else:
                        # if active length is longer than the boundary, move to the next node the current edge is pointing to, and update active edge and active length so they point to the same position
                        # this approach ensures that the skipcountpointer can always go to the correct diverging edges an active node has
                        self.active_length -= boundary
                        self.active_edge += boundary
                        self.active_node = edge.to_node
                        continue

                # No edge found for current letter(active edge) from the active node
                else:
                    # RULE 2: Create new edge
                    # If in the same phase, link prev_node to the active node
                    if self.prev_node is not None:
                        self.prev_node.suffix_link = self.active_node
                    # Create a new edge from active node
                    edge = Edge(self.active_node, i, i - self.remainder + 1)
                    self.active_node.children_edge[char_index] = edge
                    self.prev_node = None

                # update active point to the suffix link of the active node
                self.active_node = self.active_node.suffix_link

                # one extension step done, decrement remainder
                self.remainder -= 1

            # phase ends, set prev_node to None
            self.prev_node = None

    # Traverse the suffix trie using DFS, to construct the suffix array in lexigraphical order
    def dfs(self, n):
        for i in range(91):
            x = n.children_edge[i]
            if x:
                if x._end is None:  # means it is a leaf
                    self.suffix_array.append(x.end_index)
                else:
                    self.dfs(x.to_node)
