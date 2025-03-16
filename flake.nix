{
  description = "pre-commit hooks";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { ... }@inputs:
    inputs.flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = inputs.nixpkgs.legacyPackages.${system};
        formatter = pkgs.nixfmt-rfc-style;
      in
      {
        formatter = formatter;

        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            python3
            ruff
            just
            pre-commit
            python312Packages.pytest-cov
            python312Packages.pytest
          ];
          PYTHONDONTWRITEBYTECODE = 1;
        };
      }
    );
}
