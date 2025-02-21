"""Api related constants."""

# Maximum allowed sum of uploaded files.
MAX_SETUP_FILES_SIZE = 1024 * 1024 * 250  # 250 MB

# Allowed file types for computation
ALLOWED_FILE_TYPES = ["cif", "mol2", "pdb", "mmcif", "sdf"]

# Extension of output cif files containing computed charges
CHARGES_OUTPUT_EXTENSION = ".fw2.cif"
