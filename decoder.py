import sys
from bitarray import bitarray
from helper import *

# TreeNode class to be used when constructing BinaryTree for huffman code
class TreeNode:
    def __init__(self):
        self.char = None
        self.left = None
        self.right = None
        self.leaf = False

# BinaryTree that store the huffman code based on known path
class BinaryTree:
    def __init__(self):
        self.root = TreeNode()

    # Add a node to the huffman tree based on the given bit sequence
    def add_node(self, char, bit_sequence):
        current_node = self.root

        # Traverse through the given path
        for i in bit_sequence:
            if i: 
                # go to the right child
                if current_node.right is None:
                    current_node.right = TreeNode()
                current_node = current_node.right
            else:
                # go to the left child
                if current_node.left is None:
                    current_node.left = TreeNode()
                current_node = current_node.left

        # When finish traversing, set the character to the leaf node
        current_node.leaf = True
        current_node.char = char

    # Retrieve the next node based on the given bit
    def get_next_node(self, last_node, bit):
        return last_node.right if bit else last_node.left

### MAIN CLASS ###
# Decode the input .bin file using run-length decoding
class RunLengthDecoder:
    def __init__(self, file):
        # convert .bin file to bitarray
        self.bit_string = self.file_to_bitarray(file)
        self.length = len(self.bit_string)
        # pointer to current position of the bit_string which is being decoded
        self.curr_pos = 0
        # build a huffman tree for decoding process
        self.binary_tree = BinaryTree()
        # decode the header part
        self.decode_header()
        # decode the data part
        self.decoded_data = self.decode_data()
        # inverse BWT to original data
        self.original_data = self.inverse_bwt()
        # output decoded data to file
        self.output()

    # Convert .bin file to bitarray to be decoded
    def file_to_bitarray(self, filename):
        bit_data = bitarray()  # Create an empty bitarray to store the data
        with open(filename, "rb") as bin_file:
            bit_data.fromfile(bin_file)  # Read the binary file directly into the bitarray
        return bit_data

    # Decode header part
    def decode_header(self):
        # decode length of the original data using elias
        self.decoded_length = self.elias_decoding()
        # decode the number of unique characters in the original data
        uniq_chars_count = self.elias_decoding()

        for _ in range(uniq_chars_count):
            # get the ascii code (7-bits)
            ascii_code_char = bitarray()
            # use for loop to avoid slicing
            for i in range(7):
                ascii_code_char += str(self.bit_string[self.curr_pos + i])
            # convert ascii code to char
            char = chr(binary_to_decimal(ascii_code_char))  
            # move pointer to next 7-bits
            self.curr_pos += 7
            # find length of the huffman code
            huffman_length = self.elias_decoding()
            # get huffman code of the character
            huffman_code = bitarray()
            # use for loop to avoid slicing
            for i in range(huffman_length):
                huffman_code += str(self.bit_string[self.curr_pos + i])
            # move pointer based on the computed huffman length
            self.curr_pos += huffman_length
            # insert into the bit path tree based on the decoded huffman code of the character
            self.binary_tree.add_node(char, huffman_code)


    # Decode data part
    def decode_data(self):
        decoded_data = ""
        # initialize the current node to the root of the bit path tree
        current_node = self.binary_tree.root

        # Iterate the bit path tree until all the data from the remaining bit string is decoded
        while True:
            # Iterate through the bit path tree until reach leaf node
            current_node = self.binary_tree.get_next_node(current_node, self.bit_string[self.curr_pos])
            self.curr_pos += 1
            # if reach leaf node, decode the elias code to get the run length of the char
            if current_node.leaf:
                elias_runlen = self.elias_decoding()
                # character is repeated based on the run length
                decoded_data += current_node.char * elias_runlen
                # reset the current node to the root
                current_node = self.binary_tree.root
                # return the decoded data if the length is equal to the original data length
                if len(decoded_data) == self.decoded_length:
                    return decoded_data

            if self.curr_pos >= self.length - 1:
                return decoded_data

    # Decode elias code, while updating the self.curr_pos pointer
    def elias_decoding(self):
        # flag to check if elias code is done
        elias = True
        # initialize decoding result to bitarray
        decode_res = bitarray('0')
        while elias:
            # length of next segment to decode
            next_len = binary_to_decimal(decode_res) + 1
            decode_res = bitarray()

            for i in range(next_len):
                if i == 0:
                    # if the first bit is 1, then this is the last segment to decode
                    if self.bit_string[self.curr_pos]:
                        elias = False
                    else:
                        # make the first bit '1'
                        decode_res += bitarray('1')
                        continue
                # append the current bit to the decoding result
                decode_res += bitarray([self.bit_string[self.curr_pos+i]])

            # update curr_pos pointer
            self.curr_pos += next_len 
        
        # return the decoded elias code in decimal number
        return binary_to_decimal(decode_res) 
    
    # Inverse BWT string using LF-mapping method
    def inverse_bwt(self):
        # get the last column
        L = self.decoded_data
        
        frequency = [0] * 91  # store frequency of each character
        rank = [None] * 91  # store rank of each unique character
        order = [0] * len(L)  # store order of the same character

        for i in range(len(L)):
            frequency[ord(L[i]) - 36] += 1
            # order is calculated based on the frequency of each character at that index
            order[i] = frequency[ord(L[i]) - 36]

        # calculate rank
        prev_freq = 0
        prev_rank = 0
        for i in range(91):
            if frequency[i] != 0:
                rank[i] = prev_rank + prev_freq
                prev_freq = frequency[i]
                prev_rank = rank[i]

        # rebuild the string by appending the next character to the front of the string
        rebuild_string = "$"
        next_position = 0
        while len(rebuild_string) < len(L):
            rebuild_string = L[next_position] + rebuild_string
            # find the next position by using the current position's rank and order
            next_position = rank[ord(L[next_position]) - 36] + order[next_position] - 1
        return rebuild_string
            
            
    # Output the decoded data to a file
    def output(self):
        with open('q2_decoder_output.txt', "w+") as file:
            file.write(self.original_data)
                    
if __name__ == "__main__":
    RunLengthDecoder(sys.argv[1])
   