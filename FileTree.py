class FileTree:
    class Node:
        def __init__(self, name: str, is_dir: bool, parent: FileTree.Node = None, children: dict = None,
                     location: list = None):
            self.children = children
            self.parent = parent
            self.name = name
            self.is_dir = is_dir
            self.location = location

    def __init__(self):
        self.root = FileTree.Node('/', True)

    def add_node(self, path: str, is_dir: bool, location: list):
        paths = path.split('/')[1:]
        current_node = self.root
        for p in paths[:-1]:
            current_node = current_node.children.get(p)
        current_node.children.update({path: FileTree.Node(path, is_dir, current_node, location=location)})

    def search_node(self, path: str):
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node != None:
            return current_node.location

