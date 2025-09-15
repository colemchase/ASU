#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: Chase Coleman

# Perform Zig-Zag rotation on a Splay Tree

class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

class SplayTree:
    def __init__(self):
        self.root = None

    def right_rotate(self, x):
        y = x.left          # grab x's left child
        x.left = y.right    # move y's right subtree into x's left slot
        y.right = x         # make x the right child of y
        return y            # y is now the new root of this subtree

    def left_rotate(self, x):
        y = x.right # grab x's right child
        x.right = y.left # move y's left child to x's right slot
        y.left = x # make x the left child of y
        return y # y is not the new root 

    def splay(self, root, key):
        if not root or root.key == key:
            return root

        # Key lies in the left subtree
        if key < root.key:
            if not root.left:
                return root
            # Zig-Zig 
            if key < root.left.key:
                root.left.left = self.splay(root.left.left, key)
                root = self.right_rotate(root)
            # Zig Zag
            elif key > root.left.key:
                root.left.right = self.splay(root.left.right, key)
                if root.left.right:
                    root.left = self.left_rotate(root.left)
            return root if not root.left else self.right_rotate(root) # final rotation

        # Key lies in the right subtree
        if key > root.key:
            if not root.right:
                return root
            # Zag Zig
            if key < root.right.key:
                root.right.left = self.splay(root.right.left, key)
                if root.right.left:
                    root.right = self.right_rotate(root.right)
            # Zag-Zag 
            elif key > root.right.key:
                root.right.right = self.splay(root.right.right, key)
                root = self.left_rotate(root)
            return root if not root.right else self.left_rotate(root) # final rotation

    def search(self, key):
        self.root = self.splay(self.root, key)
        return self.root and self.root.key == key

    def preorder(self, root):
        if root:
            print(root.key, end=" ")
            self.preorder(root.left)
            self.preorder(root.right)


# Example Usage
tree = SplayTree()

# Example manual tree setup
tree.root = Node(30)
tree.root.left = Node(20)
tree.root.right = Node(40)
tree.root.left.left = Node(10)
tree.root.left.right = Node(25)

print("\nSearching for 25...")
found = tree.search(25)
print("Found:", found)
print("Preorder after search:")
tree.preorder(tree.root)
