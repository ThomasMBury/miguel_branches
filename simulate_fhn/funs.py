#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2 June, 2024

Functions for simulation on branch geometry

@author: tbury
"""

import numpy as np
import pandas as pd

import os


def mesh_single_branch(l1=15, w1=2, l2=5, w2=3, l_solo=3, slope=1):
    """Create mesh for geometry with one horiztal branch and one branch
    at an angl theta to the horizontal branch

    Args:
        l1: length of horizotal branch
        w1: width of horizontal branch
        l2: length of angled branch in vertical direction
        w2: width of angled branch in horiztonal direction
        l_solo: length of section of horiztonal branch before angled branch begins
        slope: slope of diagonal branch

    Returns:
        np.array - two-dimensional array of cell mesh
    """

    # Warning - diagonal branch doesn't fit in the following case
    min_l1 = l_solo + w2 + l2 / slope - 1
    if l1 < min_l1:
        print(f"Warning: min l1 for diag branch to fit is {min_l1}")

    mesh = np.zeros([w1 + l2, l1])

    # Fill in horizontal channel
    mesh[:w1, :] = 1

    # fill in diagonal channel
    for y in np.arange(w1, w1 + l2):
        left_x = l_solo + (y - w1) / slope
        right_x = left_x + w2
        for x in np.arange(l1):
            if (x >= left_x) & (x < right_x):
                mesh[y, x] = 1

    return mesh


def mesh_double_branch(l1=15, w1=3, l2=5, w2=4, l_solo=3, slope=1):
    """Create mesh for geometry with one horiztal branch and two angled branches
    symmetric to one another across the horiztonal axis

    Args:
        l1: length of horizotal branch
        w1: width of horizontal branch
        l2: length of angled brances in vertical direction
        w2: width of angled branches in horiztonal direction
        l_solo: length of section of horiztonal branch before angled branch begins
        slope: slope of diagonal branches

    Returns:
        np.array - two-dimensional array of cell mesh
    """

    # Warning - diagonal branches doesn't fit in the following case
    min_l1 = l_solo + w2 + l2 / slope - 1
    if l1 < min_l1:
        print(f"Warning: min l1 for diag branch to fit is {min_l1}")

    mesh = np.zeros([w1 + 2 * l2, l1])

    # Fill in horizontal channel
    mesh[l2 : l2 + w1, :] = 1

    # fill in upper diagonal channel
    for y in np.arange(l2):
        left_x = l_solo + (l2 - y - 1) / slope
        right_x = left_x + w2
        for x in np.arange(l1):
            if (x >= left_x) & (x < right_x):
                mesh[y, x] = 1

    # fill in lower diagonal channel
    for y in np.arange(l2 + w1, l2 + w1 + l2):
        left_x = l_solo + (y - w1 - l2) / slope
        right_x = left_x + w2
        for x in np.arange(l1):
            if (x >= left_x) & (x < right_x):
                mesh[y, x] = 1
    return mesh


def mesh_double_branch_2(l1=15, w1=3, h=5, w2=4, theta=45):
    """Create mesh for geometry with one horiztal branch and two angled branches
    symmetric to one another across the horiztonal axis

    V2 differences:
        l1 defines the length of the horizontal branch prior to and after the intersection
        w2 is now the width of the digaonal branches perpendicular to their edges
        l2 no longer
        h defines the vertical length of a diagonal branch
        slope is in degrees

    Args:
        l1: length of horizotal branch
        w1: width of horizontal branch
        w2: width of angled branches in horiztonal direction
        l_solo: length of section of horiztonal branch before angled branch begins
        slope: slope of diagonal branches

    Returns:
        np.array - two-dimensional array of cell mesh
    """

    theta_rad = theta * np.pi * 2 / 360
    len_intersection = int(w2 / (np.sin(theta_rad)))

    mesh = np.zeros([2 * h + w1, 2 * l1 + len_intersection])

    # Fill in horizontal channel
    mesh[h : h + w1, :] = 1

    # fill in upper diagonal channel
    for y in np.arange(h):
        left_x = l1 + (h - y - 1) / np.tan(theta_rad)
        right_x = left_x + len_intersection
        for x in np.arange(l1, 2 * l1 + len_intersection):
            if (x >= left_x) & (x < right_x):
                mesh[y, x] = 1

    # fill in upper diagonal channel
    for y in np.arange(h + w1, 2 * h + w1):
        left_x = l1 + (y - w1 - h) / np.tan(theta_rad)
        right_x = left_x + len_intersection
        for x in np.arange(l1, 2 * l1 + len_intersection):
            if (x >= left_x) & (x < right_x):
                mesh[y, x] = 1

    return mesh


def get_connections(mesh, conductance=1):
    """
    Create dictionary to map from position index to cell index
    Get list of connections in mesh
    """

    connections = []
    rows, cols = mesh.shape

    # Get connections going right and connections going down
    directions = [(1, 0), (0, 1)]

    # Dictionary to store index of each cell
    pos_to_cell = {}

    # Assign indices to each cell
    index = 0
    for y in range(rows):
        for x in range(cols):
            if mesh[y, x] == 1:
                pos_to_cell[(y, x)] = index
                index += 1

    # Iterate through the rows and columns
    for y in range(rows):
        for x in range(cols):
            # Check if the current cell is a one
            if mesh[y, x] == 1:
                current_index = pos_to_cell[(y, x)]
                # Iterate through the directions to find neighboring cells
                for dx, dy in directions:
                    ny, nx = y + dy, x + dx
                    # Check if the neighboring cell is within bounds and is also a one
                    if (ny, nx) in pos_to_cell:
                        neighbor_index = pos_to_cell[(ny, nx)]
                        # Add connection between current cell and neighboring cell
                        connections.append((current_index, neighbor_index, conductance))

    return pos_to_cell, connections


if __name__ == "__main__":
    print("Run tests")

    mesh = mesh_double_branch_2(l1=8, w1=3, h=5, w2=3, theta=30)
    print(mesh)

    pos_to_cell, connections = get_connections(mesh)
    print(pos_to_cell)
    print(connections)
