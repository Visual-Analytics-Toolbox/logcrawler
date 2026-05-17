/*
 * Fast Directory Listing Counter (fast_ls.c)
 * A lightweight C utility that counts the number of files and directories
 * in a specified directory. This is designed to be faster than shell 'ls'
 * commands for counting purposes.
 */

// Include necessary headers for directory operations
#include <dirent.h>   // DIR, struct dirent, opendir(), readdir(), closedir()
#include <stdio.h>    // printf(), fprintf(), perror()
#include <string.h>   // strcmp() for string comparison
#include <stdlib.h>   // General utilities

/*
 * count_files: Count the number of entries in a directory
 * 
 * Arguments:
 *   path - The filesystem path to the directory to scan
 * 
 * Returns:
 *   The number of files/directories on success, or -1 on error
 * 
 * Description:
 *   Opens a directory stream, iterates through all entries, and counts them
 *   while excluding the special directory entries "." (current) and ".."
 *   (parent). Returns -1 if the directory cannot be opened.
 */
int count_files(const char *path) {
    DIR *dir;                  // Pointer to directory stream
    struct dirent *entry;      // Pointer to directory entry structure
    int count = 0;             // Counter for entries found

    // Attempt to open the directory
    dir = opendir(path);
    if (dir == NULL) {
        perror("opendir");     // Print error message describing why opendir failed
        return -1;             // Return -1 to indicate error
    }

    // Iterate through all entries in the directory
    while ((entry = readdir(dir)) != NULL) {
        // Skip the special directory entries:
        // "." = current directory, ".." = parent directory
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;          // Skip to next iteration without counting
        }
        count++;               // Increment counter for valid entry
    }

    closedir(dir);             // Close the directory stream to free resources
    return count;              // Return the total count of entries
}

/*
 * main: Entry point for the program
 * 
 * Arguments:
 *   argc - Argument count (should be 2: program name + directory path)
 *   argv - Argument vector (array of strings)
 * 
 * Returns:
 *   0 on success, 1 on error (either wrong number of arguments or directory error)
 * 
 * Description:
 *   The main function validates command-line arguments, calls count_files() to
 *   count entries in the specified directory, and outputs the count as plain text.
 *   Exit code: 0 = success, 1 = failure (invalid arguments or cannot open directory)
 */
int main(int argc, char *argv[]) {
    // Validate that exactly one argument was provided (the directory path)
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <directory>\n", argv[0]);
        return 1;  // Exit with error code
    }

    const char *target_dir = argv[1];  // Store the target directory path from arguments
    int file_count = count_files(target_dir);  // Count the files in the directory

    // Check if count_files succeeded (returns -1 on error, >= 0 on success)
    if (file_count >= 0) {
        printf("%d", file_count);  // Print the count with no trailing newline
        return 0;                  // Exit successfully
    } else {
        return 1;                  // Exit with error code if counting failed
    }
}