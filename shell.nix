with import <nixpkgs> {};
with pkgs.python310Packages;

buildPythonPackage rec {
  name = "interpolateCodePackage";
  src = /home/christopher/work/python/hello;
  propagatedBuildInputs = [ python310Packages.pytest-shutil pkgs.python310Packages.GitPython ];
}