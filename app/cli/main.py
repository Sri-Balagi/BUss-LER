import argparse
import sys
from app.cli.commands import create_module, list_modules, validate, doctor

def main():
    parser = argparse.ArgumentParser(description="BizOS Developer CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # create-module
    create_parser = subparsers.add_parser("create-module", help="Create a new BizOS module")
    create_parser.add_argument("name", help="Name of the module (e.g., airline)")
    create_parser.add_argument("--reference", action="store_true", help="Apply a reference implementation")
    create_parser.add_argument("--template", help="Template to inherit from (e.g., retail)")
    create_parser.add_argument("--force", action="store_true", help="Force overwrite existing module")
    
    # regenerate
    regenerate_parser = subparsers.add_parser("regenerate", help="Safely regenerate an existing module's cognition.py")
    regenerate_parser.add_argument("name", help="Name of the module to regenerate")
    
    # list-modules
    list_parser = subparsers.add_parser("list-modules", help="List installed modules")
    
    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate modules")
    
    # doctor
    doctor_parser = subparsers.add_parser("doctor", help="Check BizOS health")
    
    args = parser.parse_args()
    
    if args.command == "create-module":
        create_module.run(args)
    elif args.command == "regenerate":
        # regenerate is basically create-module with --reference and --force
        args.reference = True
        args.force = True
        create_module.run(args)
    elif args.command == "list-modules":
        list_modules.run(args)
    elif args.command == "validate":
        validate.run(args)
    elif args.command == "doctor":
        doctor.run(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
