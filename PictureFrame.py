#!/usr/bin/env python
# coding=utf-8
#
"""
Generate Laser Cut Vector to Make Picture Frame.
"""

import math
import svgwrite
import os
import sys
from PySide2 import QtWidgets, QtGui
import webbrowser

X, Y = range(2)

class InputDialog(QtWidgets.QDialog):
    
    def __init__(self):
        super().__init__()
        self.input_vars = {
            "width_base": 150.0,
            "height_base": 150.0,
            "thickness_plate": 4.0,
            "gap_plate": 6.0,
            "top_rad": 35,
            "width_arc": 20,
            "height_arc": 25,
            "num_frame": 1
        }
        self.initUI()

    def initUI(self):
        layout = QtWidgets.QHBoxLayout()
        input_form = QtWidgets.QFormLayout()
        for key in self.input_vars:
            line_edit = QtWidgets.QLineEdit()
            input_form.addRow(key, line_edit)
            exec(f"self.{key}_le = line_edit")
        submit_btn = QtWidgets.QPushButton("Submit")
        submit_btn.clicked.connect(self.submit)
        input_form.addWidget(submit_btn)
        layout.addLayout(input_form)
        help_label = QtWidgets.QLabel()
        help_pixmap = QtGui.QPixmap("img/pictframe_help.png")
        help_label.setPixmap(help_pixmap)
        layout.addWidget(help_label)
        self.setLayout(layout)

    def submit(self):
        for key in self.input_vars:
            exec(f"self.input_vars[\'{key}\'] = float(self.{key}_le.text())")

        # validation = self.validate_input()
        # if validation["failed"]:
        #     QtWidgets.QMessageBox.warning(self, "Warning", validation["message"] + "Please try again.")
        #     return

        self.accept()
        obj_frame = PictureFrame(dialog.input_vars)
        obj_frame.draw_pictframe()
        obj_frame.dwg_new.save()
        path_base = os.getcwd()
        webbrowser.open("file://" + os.path.join(path_base, "lasercut_spherebase.svg"))

    def validate_input(self):
        has_failed = False
        message = ""
        return {"failed": has_failed, "message": message}


class PictureFrame():
    def __init__(self, input_results):
        self.width_base = input_results["width_base"]
        self.height_base = input_results["height_base"]
        self.t_plate = input_results["thickness_plate"]
        self.gap_plate = input_results["gap_plate"]
        self.top_rad = input_results["top_rad"]
        self.width_arc = input_results["width_arc"]
        self.height_arc = input_results["height_arc"]
        self.num_frame = int(input_results["num_frame"])
        self.dwg_new = svgwrite.Drawing("lasercut_pictframe.svg", size=("600mm", "450mm"), viewBox=("0 0 600 450"))
        self.bot_arc = math.sqrt(self.top_rad ** 2 - self.width_arc ** 2) - self.top_rad + self.height_arc

    def draw_pictframe(self):
        org_point = [3, 3]

        num_arc_h = int((self.width_base - math.sqrt(2) * self.t_plate - 2 * self.width_arc) // (self.gap_plate + self.t_plate))
        num_arc_v = int((self.height_base - math.sqrt(2) * self.t_plate - 2 * self.width_arc) // (self.gap_plate + self.t_plate))

        for j in range(0, 2):
            for i in range(0, num_arc_h):
                self.dwg_new.add(self.make_arcplate_path(self.top_rad, self.height_arc, self.width_arc, self.t_plate, org_point, self.num_frame))
                org_point[Y] = org_point[Y] + self.height_arc + 3

            org_point[X] = org_point[X] + self.width_arc + 3
            org_point[Y] = 3

            for i in range(0, num_arc_v):
                self.dwg_new.add(self.make_arcplate_path(self.top_rad, self.height_arc, self.width_arc, self.t_plate, org_point, self.num_frame))
                org_point[Y] = org_point[Y] + self.height_arc + 3

            org_point[X] = org_point[X] + self.width_arc + 3
            org_point[Y] = 3

        for i in range(0, 4):
            self.dwg_new.add(self.make_cornerarc_path(self.top_rad, self.height_arc, self.width_arc, self.t_plate, org_point))
            org_point[Y] = org_point[Y] + self.height_arc + 3

        org_point[X] = org_point[X] + self.width_arc * math.sqrt(2) + 3
        org_point[Y] = 3

        for j in range(0, 2):
            for i in range(0, self.num_frame):
                ymid_frame = self.height_arc * (i + 1) / (self.num_frame + 1) + self.t_plate / 2
                if ymid_frame + self.t_plate / 2 > self.bot_arc:
                    width_frame = math.sqrt(self.top_rad ** 2 - (self.top_rad - self.height_arc + ymid_frame + self.t_plate / 2) ** 2)
                else:
                    width_frame = self.width_arc
                self.dwg_new.add(self.make_frame_path(width_frame, self.width_base - math.sqrt(2) * self.t_plate, self.t_plate, self.gap_plate, org_point, num_arc_h))
                org_point[X] = org_point[X] + width_frame + 3
                self.dwg_new.add(self.make_frame_path(width_frame, self.height_base - math.sqrt(2) * self.t_plate, self.t_plate, self.gap_plate, org_point, num_arc_v))
                org_point[X] = org_point[X] + width_frame + 3

        self.dwg_new.add(self.make_pictplate_component(self.width_base, self.height_base, self.t_plate, self.width_arc, self.gap_plate, org_point, num_arc_h, num_arc_v))


    def make_cornerarc_path(self, top_rad, height_plate, width_plate, t_plate, org_point):

        str_path = ""
        str_path += "M {0},{1}".format(org_point[X], org_point[Y] + t_plate)

        bot_arc = math.sqrt(top_rad ** 2 - width_plate ** 2) - top_rad + height_plate

        # top arc
        str_path += " L {0},{1}".format(org_point[X], org_point[Y] + height_plate)
        str_path += " A {0},{1} 0 0,0 {2},{3}".format(top_rad * math.sqrt(2), top_rad, org_point[X] + width_plate * math.sqrt(2), org_point[Y] + bot_arc)
        str_path += " L {0},{1}".format(org_point[X] + width_plate * math.sqrt(2), org_point[Y] + t_plate)

        # bump for base
        str_path += " L {0},{1}".format(org_point[X] + (width_plate * math.sqrt(2) + t_plate) / 2, org_point[Y] + t_plate)
        str_path += " L {0},{1}".format(org_point[X] + (width_plate * math.sqrt(2) + t_plate) / 2, org_point[Y])
        str_path += " L {0},{1}".format(org_point[X] + (width_plate * math.sqrt(2) - t_plate) / 2, org_point[Y])
        str_path += " L {0},{1}".format(org_point[X] + (width_plate * math.sqrt(2) - t_plate) / 2, org_point[Y] + t_plate)

        # back to origin
        str_path += " L {0},{1}".format(org_point[X], org_point[Y] + t_plate)
        path_add = self.dwg_new.path(d=str_path, fill="none", style="stroke:#000000;stroke-width:0.3")
        return path_add

    def make_arcplate_path(self, top_rad, height_plate, width_plate, t_plate, org_point, num_frame):

        str_path = ""
        str_path += "M {0},{1}".format(org_point[X], org_point[Y] + t_plate)

        # dents for frames
        for i in range(0, num_frame):
            ymid_frame = height_plate * (i + 1) / (num_frame + 1) + t_plate / 2
            if ymid_frame + t_plate / 2 > self.bot_arc:
                depth_dent = math.sqrt(top_rad ** 2 - (top_rad - height_plate + ymid_frame + t_plate / 2) ** 2) / 2
            else:
                depth_dent = width_plate / 2
            str_path += " L {0},{1}".format(org_point[X], org_point[Y] + ymid_frame - t_plate / 2)
            str_path += " L {0},{1}".format(org_point[X] + depth_dent, org_point[Y] + ymid_frame - t_plate / 2)
            str_path += " L {0},{1}".format(org_point[X] + depth_dent, org_point[Y] + ymid_frame + t_plate / 2)
            str_path += " L {0},{1}".format(org_point[X], org_point[Y] + ymid_frame + t_plate / 2)

        # top arc
        str_path += " L {0},{1}".format(org_point[X], org_point[Y] + height_plate)
        str_path += " A {0},{0} 0 0,0 {1},{2}".format(top_rad, org_point[X] + width_plate, org_point[Y] + self.bot_arc)
        str_path += " L {0},{1}".format(org_point[X] + width_plate, org_point[Y] + t_plate)

        # bump for base
        str_path += " L {0},{1}".format(org_point[X] + (width_plate + t_plate) / 2, org_point[Y] + t_plate)
        str_path += " L {0},{1}".format(org_point[X] + (width_plate + t_plate) / 2, org_point[Y])
        str_path += " L {0},{1}".format(org_point[X] + (width_plate - t_plate) / 2, org_point[Y])
        str_path += " L {0},{1}".format(org_point[X] + (width_plate - t_plate) / 2, org_point[Y] + t_plate)

        # back to origin
        str_path += " L {0},{1}".format(org_point[X], org_point[Y] + t_plate)
        path_add = self.dwg_new.path(d=str_path, fill="none", style="stroke:#000000;stroke-width:0.3")
        return path_add


    def make_frame_path(self, width_frame, length_frame, t_plate, gap_plate, org_point, num_arc):
        
        str_path = ""
        str_path += "M {0},{1}".format(org_point[X], org_point[Y])
        str_path += " L {0},{1}".format(org_point[X] + width_frame, org_point[Y] + width_frame)

        for i in range(0, num_arc):
            ymid_arc = org_point[Y] + length_frame / 2 + (i - (num_arc - 1) / 2) * (gap_plate + t_plate)
            str_path += " L {0},{1}".format(org_point[X] + width_frame, ymid_arc - t_plate / 2)
            str_path += " L {0},{1}".format(org_point[X] + width_frame / 2, ymid_arc - t_plate / 2)
            str_path += " L {0},{1}".format(org_point[X] + width_frame / 2, ymid_arc + t_plate / 2)
            str_path += " L {0},{1}".format(org_point[X] + width_frame, ymid_arc + t_plate / 2)

        # back to origin
        str_path += " L {0},{1}".format(org_point[X] + width_frame, org_point[Y] + length_frame - width_frame)
        str_path += " L {0},{1}".format(org_point[X], org_point[Y] + length_frame)
        str_path += " L {0},{1}".format(org_point[X], org_point[Y])
        path_add = self.dwg_new.path(d=str_path, fill="none", style="stroke:#000000;stroke-width:0.3")
        return path_add


    def make_pictplate_component(self, width_base, height_base, t_plate, width_arc, gap_plate, org_point, num_arc_w, num_arc_h):
        
        group_add = self.dwg_new.g(id="pictplate")
        group_add.add(self.make_base_path(width_base, height_base, org_point))
        
        center_hole = [0, 0]
        for i in range(0, num_arc_h):
            center_hole[Y] = org_point[Y] + height_base / 2 + (i - (num_arc_h - 1) / 2) * (gap_plate + t_plate)
            center_hole[X] = org_point[X] + width_arc / 2
            group_add.add(self.make_hole_path(t_plate, 0, center_hole))
            center_hole[X] = org_point[X] + width_base - width_arc / 2
            group_add.add(self.make_hole_path(t_plate, 0, center_hole))
        for i in range(0, num_arc_w):
            center_hole[X] = org_point[X] + width_base / 2 + (i - (num_arc_w - 1) / 2) * (gap_plate + t_plate)
            center_hole[Y] = org_point[Y] + width_arc / 2
            group_add.add(self.make_hole_path(t_plate, 0, center_hole))
            center_hole[Y] = org_point[Y] + height_base - width_arc / 2
            group_add.add(self.make_hole_path(t_plate, 0, center_hole))

        center_hole[X] = org_point[X] + width_arc / 2 + t_plate / (2 * math.sqrt(2))
        center_hole[Y] = org_point[Y] + width_arc / 2 + t_plate / (2 * math.sqrt(2))
        group_add.add(self.make_hole_path(t_plate, 45, center_hole))
        center_hole[Y] = org_point[Y] + height_base - width_arc / 2 - t_plate / (2 * math.sqrt(2))
        group_add.add(self.make_hole_path(t_plate, 45, center_hole))
        center_hole[X] = org_point[X] + width_base - width_arc / 2 - t_plate / (2 * math.sqrt(2))
        group_add.add(self.make_hole_path(t_plate, 45, center_hole))
        center_hole[Y] = org_point[Y] + width_arc / 2 + t_plate / (2 * math.sqrt(2))
        group_add.add(self.make_hole_path(t_plate, 45, center_hole))

        return group_add


    def make_base_path(self, width_base, height_base, org_point):
        str_path = ""
        str_path += "M {0},{1}".format(org_point[X], org_point[Y])
        str_path += " L {0},{1}".format(org_point[X] + width_base, org_point[Y])
        str_path += " L {0},{1}".format(org_point[X] + width_base, org_point[Y] + height_base)
        str_path += " L {0},{1}".format(org_point[X], org_point[Y] + height_base)
        str_path += " L {0},{1}".format(org_point[X], org_point[Y])
        path_add = self.dwg_new.path(d=str_path, fill="none", style="stroke:#000000;stroke-width:0.3")
        return path_add


    def make_hole_path(self, size, rot, center):
        angle_rad = math.radians(rot)
        half_size = size / 2
        # points without rotation
        points = [
            (-half_size, -half_size),
            (half_size, -half_size),
            (half_size, half_size),
            (-half_size, half_size)
        ]
        # apply rotation
        rotated_points = [
            (
                center[X] + x * math.cos(angle_rad) - y * math.sin(angle_rad),
                center[Y] + x * math.sin(angle_rad) + y * math.cos(angle_rad)
            )
            for x, y in points
        ]
        str_path = "M" + " L".join([f"{x},{y}" for x, y in rotated_points]) + " Z"
        path_add = self.dwg_new.path(d=str_path, fill="none", style="stroke:#FF0000;stroke-width:0.3")
        return path_add


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    dialog = InputDialog()
    dialog.show()
    sys.exit(app.exec_())