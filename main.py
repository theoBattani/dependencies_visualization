import os, sys

from diagrams import Cluster, Diagram
from diagrams.programming.framework import Spring
from diagrams.programming.language import Java
from diagrams.programming.flowchart import Database

class Package:
  def __init__(self, name, parent=None):
    self.name = name
    self.parent = parent
    if parent:
      parent.append_child(name, self)
    self.children = {}
    self.classes = {}
  
  def append_child(self, name, child):
    self.children[name] = child
  
  def append_class(self, name):
    if name not in self.classes.keys():
      self.classes[name] = JavaClass(name, package=self)
    return self.classes[name]
  
  def has_parent(self):
    return self.parent != None

  def has_children(self):
    return self.children != {}

  def get_full_name(self):
    if not self.has_parent():
      return self.name
    else:
      return f"{self.parent.get_full_name()}.{self.name}"

  def get_dependencies():
    dependencies = []
    for clazz in self.classes.values():
      for dependency in clazz.package:
        dependencies.append(dependency)
    return dependencies

  def make_nodes(self):
    print(f"making {self.name} diagram")
    with Cluster(self.name):
      nodes = []
      for clazz in self.classes.values():
        nodes.append(clazz.make_node())
      for child in self.children.values():
        child.make_nodes()

  def connect_nodes(self):
    print(f"in {self.name} connect nodes")
    for clazz in self.classes.values():
      print(clazz.name)
      clazz.get_dependencies_nodes() >> clazz.node
    for child in self.children.values():
      child.connect_nodes()

class JavaClass:
  def __init__(self, name, package=None):
    self.name = name
    self.package = package
    self.dependencies = {}
    self.node = None

  def add_dependency(self, dependency):
    self.dependencies[dependency.name] = dependency
  
  def get_dependencies_nodes(self):
    return [d.node for d in self.dependencies.values()]
  
  def make_node(self):
    if not self.node:
      self.node = Java(self.name)
    return self.node

class Project:
  def __init__(self, name):
    self.name = name
    self.packages = {}

  def add_package(self, name, package):
    self.packages[name] = package

  def add_package_by_full_name(self, package_name):
    names = package_name.split('.')
    p = None
    # print(l, file=sys.stderr, flush=True)
    name = names.pop(0)
    if name not in list(self.packages.keys()):
      p = Package(name)
      self.packages[name] = p
    else:
      p = self.packages[name]
    while names != []:
      name = names.pop(0)
      if name not in list(p.children.keys()):
        pp = Package(name, parent=p)
        # p.append_child(name, pp)
        p = pp
      else:
        p = p.children[name]
    return p

  def parse_repository(self, path):
    try:
      os.chdir(f"{path}\\src\\main\\java")
    except:
      print("Error: Not a java project", file=sys.stderr, flush=True)
      sys.exit()

    for path, directories, files in os.walk("."):
      # print((path, directories, files), file=sys.stderr, flush=True)
      # print(path, file=sys.stderr, flush=True)
      # print(directories, file=sys.stderr, flush=True)
      # [print("  " + d, file=sys.stderr, flush=True) for d in directories]
      # [print("  " + f, file=sys.stderr, flush=True) for f in  files]
      
      # splitted_path = path.split('\\')
      # splitted_path.pop(0)
      # print(splitted_path)

      for file in files:
        # print(file, file=sys.stderr, flush=True)
        if file.split(".")[1] == "java":
          with open(f"{path}\\{file}", 'r') as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
              l = line.split()
              if len(l) > 0:
                if l[0] == "package":
                  package = l[1][:-1]
                  p = self.add_package_by_full_name(package)
                  # print((p.get_full_name(), p))
                  classname = file.split('.')[0]
                  # print(clazz, file=sys.stderr, flush=True)
                  clazz = p.append_class(classname)
                if l[0] == "import":
                  dependency = l[1]
                  dependency = dependency[:-1]
                  # print(dependency.split('.'), file=sys.stderr, flush=True)
                  *d_package, d_name = dependency.split('.')
                  # print(f"{d_clazz} {d_package}", file=sys.stderr, flush=True)
                  d_p = self.add_package_by_full_name('.'.join(d_package))
                  d_clazz = d_p.append_class(d_name)
                  clazz.add_dependency(d_clazz)
                  # if d_clazz not in d_p.classes.keys():
                  #   dependency = JavaClass(d_clazz)
                  #   d_p.append_class(d_clazz, dependency)
                  #   clazz.add_dependency(dependency)

  def make_nodes(self):
    print("making project diagram ...")
    for name, package in self.packages.items():
      package.make_nodes()
    
  def connect_nodes(self):
    print("in project connect nodes")
    for package in self.packages.values():
      package.connect_nodes()

  def make_diagram(self, targetDir):
    os.chdir(targetDir)
    with Diagram(self.name, show=True):
      self.make_nodes()
      self.connect_nodes()


def main(args):

  currentDir = os.getcwd()

  if len(args) == 1:
    print("Error: No such file or directory", file=sys.stderr, flush=True)
    sys.exit()

  project = Project(args[1].split('\\').pop())
  project.parse_repository(sys.argv[1])
  project.make_diagram(currentDir)

  # print(project.name, file=sys.stderr, flush=True)
  # print(project.packages, file=sys.stderr, flush=True)

if __name__ == '__main__':
  main(sys.argv)