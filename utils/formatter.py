def format_output(data, indent=0):
    """
    Convert dict/list into clean terminal-style output
    """

    space = "  " * indent

    if isinstance(data, dict):
        lines = []
        for key, value in data.items():

            # Nested structures
            if isinstance(value, (dict, list)):
                lines.append(f"{space}{key}:")
                lines.append(format_output(value, indent + 1))

            else:
                lines.append(f"{space}{key:<18} : {value}")

        return "\n".join(lines)

    elif isinstance(data, list):
        lines = []
        for item in data:

            if isinstance(item, (dict, list)):
                lines.append(format_output(item, indent + 1))
            else:
                lines.append(f"{space}- {item}")

        return "\n".join(lines)

    else:
        return f"{space}{data}"