# Edit the monorepo project `.Renviron` in your configured R editor.
# This keeps API keys and local machine paths in the project-level env file
# that the existing ETL scripts already load before running.

library(usethis)

# Open the repo's project-scoped `.Renviron` file so local secrets and paths
# can be updated without hunting for the file manually.
usethis::edit_r_environ(scope = "project")
