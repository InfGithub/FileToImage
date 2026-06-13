# bud.py

import ast, black

class FromImportNodeTransformer(ast.NodeTransformer):
    def __init__(self, file_names):
        self.from_imports = dict()
        self.file_names = file_names
        self.module_set = set()

    def visit_ImportFrom(self, node):
        module = node.module
        level = node.level

        if node.col_offset > 0:
            return node

        if module in self.file_names:
            return None

        imported_names = set()
        for alias in node.names:
            imported_names.add((alias.name, alias.asname))

        if module in self.module_set:
            self.from_imports[module]["names"].update(imported_names)
            return None
        else:
            self.module_set.add(module)
            self.from_imports[module] = {
                "module": module,
                "level": level,
                "names": imported_names,
            }
        return None

class ImportNodeTransformer(ast.NodeTransformer):
    def __init__(self, file_names):
        self.file_names = file_names
        self.imports = dict()

    def visit_Import(self, node):
        if node.col_offset > 0:
            return node

        for alias in list(node.names):
            if alias.name in self.file_names:
                node.names.remove(alias)

        if not node.names:
            return None

        for alias in node.names:
            if alias.name not in self.imports:
                self.imports[alias.name] = alias
        return None

class IfVisitor(ast.NodeVisitor):
    def __init__(self):
        self.ifs = list()
    def visit_If(self, node):
        if not isinstance(node.test, ast.Compare):
            return
        if not isinstance(node.test.left, ast.Name):
            return
        if not node.test.left.id == "__name__":
            return
        self.ifs.append(node)

class IfTransformer(ast.NodeTransformer):
    def __init__(self, ifs):
        self.ifs = set(ifs[:-1]) if len(ifs) > 1 else set()
    def visit_If(self, node):
        if node in self.ifs:
            return None
        return node

def main():
    files = [
        "compress.py",
        "cryption.py",
        "data.py",
        "util.py",
        "core.py",
        "ui.py",
        "main.py",
    ]

    file_names = [n.replace(".py", "") for n in files]
    output = "file2img.py"

    codes = []
    for name in files:
        with open(name, mode="r", encoding="utf-8") as f:
            codes.append(f.read())

    code = "\n\n".join(codes)

    tree = ast.parse(code)

    from_transformer = FromImportNodeTransformer(file_names)
    from_transformer.visit(tree)

    import_transformer = ImportNodeTransformer(file_names)
    import_transformer.visit(tree)

    if_visitor = IfVisitor()
    if_visitor.visit(tree)
    if_transformer = IfTransformer(if_visitor.ifs)
    if_transformer.visit(tree)

    all_imports = []

    sorted_from = sorted(from_transformer.from_imports.items(), key=lambda x: x[0])
    for module, info in sorted_from:
        names = sorted(info["names"], key=lambda n: n[0])
        aliases = [ast.alias(name=name, asname=asname) for name, asname in names]
        import_node = ast.ImportFrom(
            module=module,
            names=aliases,
            level=info["level"]
        )
        all_imports.append(import_node)

    if import_transformer.imports:
        sorted_aliases = sorted(import_transformer.imports.values(), key=lambda a: a.name)
        for alias in sorted_aliases:
            all_imports.append(ast.Import(names=[alias]))

    def import_key(node):
        if isinstance(node, ast.ImportFrom):
            return (0, node.module or "")
        else:
            return (1, node.names[0].name)
    all_imports.sort(key=import_key)

    for node in reversed(all_imports):
        tree.body.insert(0, node)

    ast.fix_missing_locations(tree)

    final_code = ast.unparse(tree)

    header = f"# Auto-generated {output} by bud.py\n# Source files: {', '.join(files)}\n\n"
    final_code = header + final_code

    final_code = black.format_str(final_code, mode=black.Mode())

    with open(output, mode="w", encoding="utf-8") as f:
        f.write(final_code)

    print(f"Successfully generated {output}")

if __name__ == "__main__":
    main()