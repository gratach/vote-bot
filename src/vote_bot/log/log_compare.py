arbitraryContent = object()   
def containsLogTreeThisStructure(logs, structure):
    if type(structure) is dict:
        if type(logs) is not dict:
            return False
        for key, value in structure.items():
            if key not in logs:
                return False
            if not containsLogTreeThisStructure(logs[key], value):
                return False
        return True
    elif type(structure) is list:
        if type(logs) is not list:
            return False
        logListIndex = 0
        for struct_item in structure:
            if logListIndex >= len(logs):
                return False
            if not containsLogTreeThisStructure(logs[logListIndex], struct_item):
                return False
            logListIndex += 1
        return True
    elif type(structure) in [str, int, float, bool, type(None)]:
        return logs == structure
    elif structure is arbitraryContent:
        return True
    else:
        raise ValueError("Unsupported structure type for log comparison")