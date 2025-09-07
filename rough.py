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
        y = x.left
        x.left = y.right
        y.right = x
        return y

    def left_rotate(self, x):
        y = x.right
        x.right = y.left
        y.left = x
        return y

    def splay(self, root, key):
        if not root or root.key == key:
            return root

        # Key lies in the left subtree
        if key < root.key:
            if not root.left:
                return root
            # Zig-Zig (Left Left)
            if key < root.left.key:
                root.left.left = self.splay(root.left.left, key)
                if root.left.left:
                    root.left = self.left.right_rotate(root.left)
            # Zig-Zag (Left Right)
            elif key > root.left.key:
                root.left.right = self.splay(root.left.right, key)
                if root.left.right:
                    root.left = self.left.left_rotate(root.left)

            return root if not root.left else self.right_rotate(root)

        # Key lies in the right subtree
        if key > root.key:
            if not root.right
            # Zag-Zig (Right Left)


            # Zag-Zag (Right Right)


            return 

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
