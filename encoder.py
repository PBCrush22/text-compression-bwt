import heapq
import sys
from helper import *
from bitarray import bitarray

# Convert the input string to BWT, by using the suffix array computed from ukkonen suffix tree
class BWTConverter:
    def __init__(self, string):
        self.string = string
        self.implicitST = SuffixTree(string)
        self.suffix_array = self.implicitST.suffix_array

    # Convert the suffix array to BWT string
    def convert(self):
        self.result = ""
        for i in range(len(self.suffix_array)):
            self.result += self.string[self.suffix_array[i]-1]
        return self.result

# HeapNode class to represent node when constructing heap for huffman code
class HeapNode:
    def __init__(self, char, frequency, left_child=None, right_child=None): 
        self.char = char
        self.frequency = frequency 
        self.left_child = left_child  # Store HeapNode object
        self.right_child = right_child  # Store HeapNode object
        # 0 for left child, 1 for right child
        self.direction = '' 
  
    def __lt__(self, nxt): 
        return self.frequency < nxt.frequency 
    
### MAIN CLASS ###
# Encode the input string using run-length encoding
class RunLengthEncoder:
    def __init__(self, string):
        # compute the BWT of the input string
        self.string = BWTConverter(string).convert()
        self.length = len(self.string)
        # store the frequency of each unique characters in self.string
        self.uniq_chars = [None] * 91
        # store the huffman code of each unique characters in self.string
        self.huffman_heap = [None] * 91
        # store the elias code of length of huffman code word
        self.huffman_length = [None] * 91
        # get frequency of each unique characters in self.string
        self.get_frequency()
        # compute huffman word core for each unique characters populated to self.uniqueChar
        self.get_huffman_code_word()
        # encode header and data part
        self.res = self.encode_header() + self.encode_data()
        # output to file
        self.output()

    # Do elias encoding on given decimal number
    def elias_encoding(self, decimal_num):
        # Convert decimal number to binary
        elias_code = decimal_to_binary(decimal_num)
        length = len(elias_code)
        # Repeat the process until the length of the binary number is 1
        while length != 1:
            length -= 1
            encoded_bitarray = bitarray(format(length, 'b'))
            # Change the first bit to 0
            encoded_bitarray[0] = 0
            # Add the binary number in front of previous computed elias code
            elias_code = encoded_bitarray + elias_code
            length = len(encoded_bitarray)
            if length == 1:
                return elias_code
        return elias_code


    # Calculate the frequency of each unique characters in self.string and stores it in respective ascii index
    def get_frequency(self):
        for i in range(self.length):
            ascii_val = char_to_ascii(self.string[i])
            if self.uniq_chars[ascii_val] is not None:
                self.uniq_chars[ascii_val] += 1
            else:
                self.uniq_chars[ascii_val] = 1
    # Handles the computation of huffman code word for each unique characters
    def get_huffman_code_word(self):
        # build heap for huffman code, by calculating the frequency of each unique characters
        heap = self.build_huffman_heap()
        # calculate huffman code by passing the root node of the tree as parameter
        self.compute_huffman_code(heap[0])

    # Populate heap by calculating the frequency of unique characters and combining them to form a tree
    def build_huffman_heap(self):
        # heap list store the HeapNode object, HeapNode object stores info such as left and right child
        heap = []
        for i in range(91):
            if self.uniq_chars[i] is not None:
                # push frequency and character
                heapq.heappush(heap, HeapNode(ascii_to_char(i), self.uniq_chars[i]))
        while len(heap) > 1:
            # extract min
            left = heapq.heappop(heap)
            right = heapq.heappop(heap)
            left.direction = 0
            right.direction = 1
            # combine the two min frequency nodes to form a new node, push back to heap
            new_node = HeapNode(left.char + right.char, left.frequency + right.frequency, left, right)
            heapq.heappush(heap, new_node)
        return heap
    
    # Calculate the huffman code word for each unique characters by calling this recursive function
    def compute_huffman_code(self, node, val = ''):
        updated_val = val + str(node.direction) 
  
        # the process is repeated until leaf node is reached
        if(node.left_child): 
            self.compute_huffman_code(node.left_child, updated_val)
        if(node.right_child): 
            self.compute_huffman_code(node.right_child, updated_val)
  
        # if leaf node, add the huffman code word and length to the respective list
        if(not node.left_child and not node.right_child): 
            self.huffman_heap[char_to_ascii(node.char)] = bitarray(updated_val)
            # encode the length of huffman code word using elias encoding, store it in huffman_length list
            self.huffman_length[char_to_ascii(node.char)] = self.elias_encoding(len(updated_val))
        return self.huffman_heap

    # Encode header part
    def encode_header(self):
        # encode the length of the string using elias encoding
        encoded_bitarray = self.elias_encoding(self.length)
        # encode the total number of unique characters
        total_uniq_chars = sum(x is not None for x in self.uniq_chars)
        uniq_chars_count = self.elias_encoding(total_uniq_chars)
        encoded_bitarray += uniq_chars_count

        # for each unique characters, append the ASCII value of each unique characters, huffman code word length and huffman code word in order
        for i in range(91):
            if self.uniq_chars[i] is not None:
                encoded_bitarray += char_to_binary(ascii_to_char(i)) + self.huffman_length[i] + self.huffman_heap[i]

        return encoded_bitarray

    # Encode the data part
    def encode_data(self):
        # get the run-length encoding of the input string to be encoded
        encoded_tuples = self.run_length_encoding()
        # initialise the bitarray to store the encoded data
        encoded_bitarray = bitarray()
        
        # for each character and its run length, append the huffman code word and elias code of the run length to the bitarray
        for char, run_length in encoded_tuples:
            huffman = self.huffman_heap[char_to_ascii(char)]
            elias = self.elias_encoding(run_length)
            encoded_bitarray += huffman + elias

        return encoded_bitarray
    
    # Perform run-length encoding on the bwt string
    def run_length_encoding(self):
        encoded_tuples = [] # list of tuples containing (character, run_length)
        current_char = None
        current_run_length = 0

        # iterate through the bwt string, if the current character is the same as the previous character, increment the run length
        for char in self.string:
            if char == current_char:
                current_run_length += 1
            # if the current character is different from the previous character, append the previous character and its run length to the list
            else:
                if current_char is not None:
                    encoded_tuples.append((current_char, current_run_length))
                current_char = char
                current_run_length = 1
        
        encoded_tuples.append((current_char, current_run_length))
        return encoded_tuples

    # Output the encoded string to a binary file
    def output(self):
        # Change bits to bytes so that the encoded string a factor of 8
        bytes_data = self.res.tobytes()
        # write the encoded string to a binary file
        with open('q2_encoder_output.bin', "wb") as file:
            file.write(bytes_data)

if __name__ == "__main__":
    filename = sys.argv[1]
    with open(filename, "r") as file:
        string = file.read()
    if string[-1] != '$':
        string += '$'
    RunLengthEncoder(string)
