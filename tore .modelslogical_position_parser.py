[1mdiff --git a/models/logical_position_parser.py b/models/logical_position_parser.py[m
[1mindex adcd96a..27c9862 100644[m
[1m--- a/models/logical_position_parser.py[m
[1m+++ b/models/logical_position_parser.py[m
[36m@@ -1,5 +1,7 @@[m
 # models/logical_position_parser.py[m
 [m
[32m+[m[32mfrom functools import lru_cache[m
[32m+[m
 from .enums import Finger, Hand, Layer, Row[m
 from .logical_position import LogicalPosition[m
 [m
[36m@@ -47,21 +49,31 @@[m [mclass LogicalPositionParser:[m
         """[m
         Parse a logical position ID.[m
 [m
[31m-        Example[m
[31m-        -------[m
[31m-        L-M-H-2[m
[31m-[m
[31m-        ->[m
[31m-        LogicalPosition([m
[31m-            layer=Layer.L0,[m
[31m-            hand=Hand.LEFT,[m
[31m-            finger=Finger.MIDDLE,[m
[31m-            row=Row.HOME,[m
[31m-            column=2,[m
[32m+[m[32m        Equivalent position strings differing only in case or[m
[32m+[m[32m        surrounding whitespace share the same cached result.[m
[32m+[m[32m        """[m
[32m+[m
[32m+[m[32m        normalized_position_id = ([m
[32m+[m[32m            position_id.strip().upper()[m
         )[m
[32m+[m
[32m+[m[32m        return cls._parse_normalized([m
[32m+[m[32m            normalized_position_id,[m
[32m+[m[32m            layer,[m
[32m+[m[32m        )[m
[32m+[m
[32m+[m[32m    @classmethod[m
[32m+[m[32m    @lru_cache(maxsize=None)[m
[32m+[m[32m    def _parse_normalized([m
[32m+[m[32m        cls,[m
[32m+[m[32m        position_id: str,[m
[32m+[m[32m        layer: Layer,[m
[32m+[m[32m    ) -> LogicalPosition:[m
[32m+[m[32m        """[m
[32m+[m[32m        Parse and cache a normalized logical position ID.[m
         """[m
 [m
[31m-        parts = position_id.strip().upper().split("-")[m
[32m+[m[32m        parts = position_id.split("-")[m
 [m
         if len(parts) != 4:[m
             raise ValueError([m
[36m@@ -70,39 +82,54 @@[m [mclass LogicalPositionParser:[m
                 f"{position_id!r}"[m
             )[m
 [m
[31m-        hand_code, finger_code, row_code, column_code = parts[m
[32m+[m[32m        ([m
[32m+[m[32m            hand_code,[m
[32m+[m[32m            finger_code,[m
[32m+[m[32m            row_code,[m
[32m+[m[32m            column_code,[m
[32m+[m[32m        ) = parts[m
 [m
         try:[m
[31m-            hand = cls._HAND_MAP[hand_code][m
[32m+[m[32m            hand = cls._HAND_MAP[[m
[32m+[m[32m                hand_code[m
[32m+[m[32m            ][m
         except KeyError:[m
             raise ValueError([m
                 f"Unknown hand code: {hand_code!r}"[m
             ) from None[m
 [m
         try:[m
[31m-            finger = cls._FINGER_MAP[finger_code][m
[32m+[m[32m            finger = cls._FINGER_MAP[[m
[32m+[m[32m                finger_code[m
[32m+[m[32m            ][m
         except KeyError:[m
             raise ValueError([m
                 f"Unknown finger code: {finger_code!r}"[m
             ) from None[m
 [m
         try:[m
[31m-            row = cls._ROW_MAP[row_code][m
[32m+[m[32m            row = cls._ROW_MAP[[m
[32m+[m[32m                row_code[m
[32m+[m[32m            ][m
         except KeyError:[m
             raise ValueError([m
                 f"Unknown row code: {row_code!r}"[m
             ) from None[m
 [m
         try:[m
[31m-            column = int(column_code)[m
[32m+[m[32m            column = int([m
[32m+[m[32m                column_code[m
[32m+[m[32m            )[m
         except ValueError:[m
             raise ValueError([m
[31m-                f"Column must be an integer: {column_code!r}"[m
[32m+[m[32m                "Column must be an integer: "[m
[32m+[m[32m                f"{column_code!r}"[m
             ) from None[m
 [m
         if column < 0:[m
             raise ValueError([m
[31m-                f"Column must be zero or greater: {column}"[m
[32m+[m[32m                "Column must be zero or greater: "[m
[32m+[m[32m                f"{column}"[m
             )[m
 [m
         return LogicalPosition([m
