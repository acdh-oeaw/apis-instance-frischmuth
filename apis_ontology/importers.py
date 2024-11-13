from apis_core.generic.importers import GenericModelImporter


class PlaceImporter(GenericModelImporter):
    def mangle_data(self, data):
        if "wkt" in data:
            import re

            # Match coordinates in Point ( longitude latitude ) format
            match = re.match(
                r"Point\s*\(\s*([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s*\)", data["wkt"]
            )
            if match:
                data["longitude"] = float(match.group(1))
                data["latitude"] = float(match.group(2))
                del data["wkt"]
        return data
