# Changelog

All notable changes pertinent to the end user of this project will be documented in this file.

## 0.13.4 - 2026-03-17

### Changed

- Tweaked the UI

## 0.13.3 - 2026-03-17

### Fixed

- Fix mis-configured directory specification

## 0.13.2 - 2026-03-17

### Changed

- Relocated database.json to %APPDATA%\Local\FileViewer to avoid the need to keep manually copying it from one release
  folder to
  the next

## 0.13.1 - 2026-03-16

### Fixed

- Fixes an issue which caused the context menu to not work

## 0.13.0 - 2026-03-16

### Added

- Added a recents list

## 0.12.5 - 2026-03-13

### Fixed

- "My Computer" button now properly updates the titlebar path

## 0.12.4 - 2026-03-13

### Updated

- Titlebar path tweak

## 0.12.3 - 2026-03-13

### Fixed

- Fixes a regression in the titlebar path string

## 0.12.2 - 2026-03-12

### Fixed

- Fixes regression where the back and root buttons were improperly placed at the bottom of the file browser pane

## 0.12.1 - 2026-03-11

### Fixed

- Groupbox labels are now blurred

## 0.12.0 - 2026-03-11

### Added

- Main application windows is now blurred when the about dialog is shown

## 0.11.1 - 2026-03-10

### Fixed

- Fixes the / vs \ in the titlebar when clicking the back button

## 0.11.0 - 2026-03-10

### Updated

- Allows directories to be deleted

## 0.10.4 - 2026-03-05

### Updated

- Updates build script to append the version number to the deployment folder

## 0.10.3 - 2026-03-05

### Updated

- Tweaks icons
- Updates build scripts

## 0.10.2 - 2026-03-04

### Updated

- Adds more icons

## 0.10.1 - 2026-03-03

### Updated

- Updated and added icons

## 0.10.0 - 2026-03-03

### Changed

- Allows folders to be renamed

## 0.9.7 - 2026-03-02

### Fixed

- Fixes an issue where the titlebar was not updated with the new name after renaming a file

## 0.9.6 - 2026-03-02

### Fixed

- Fixes an issue where text in the about dialog was cut off

## 0.9.2 - 2026-02-27

### Fixed

- Sets zoom factor for images to 100% when loading into the viewer to account for zoom adjustment changes for previous
  image viewing

## 0.9.1 - 2026-02-26

### Fixed

- Re-ordering and re-naming are now immediately reflected in the bookmarks database

## 0.9.0 - 2026-02-25

### Changed

- Transitions to using tinydb for managing bookmarks (formally favorites)

## 0.8.1 - 2026-02-17

### Fixed

- Fixes a bug which caused opening a location in Windows Explorer to fail

## 0.8.0 - 2026-02-10

### Added

- Adds context menu option to open a file's location in Windows Explorer

## 0.7.2 - 2026-02-09

### Fixed

- Fixes a bug which prevented setting the file browser root path if that path had %XX sequences.

## 0.7.1 - 2026-02-09

### Fixed

- Fixes a bug with the makefile pyinstaller target

## 0.7.0 - 2026-02-05

### Added

- Context menu Open with Acrobat

## 0.6.0 - 2026-02-05

### Added

- Menu option to show / hide hidden files

## 0.5.0 - 2026-02-04

### Added

- A button to go all the wqy back to the root directory

## 0.4.3 - 2026-02-04

### Fixed

- Fixes a sorting issue introduced in 0.4.2
- Fixes a rootpath issue which did not show other drives and network maps

## 0.4.2 - 2026-02-04

### Fixed

- Fixes titlebar updating
- Fixes rootpath issue on Windows

## 0.4.1

### Fixed

- Fixed Email line in About dialog being cut in half.

## 0.4.0

### Changed

- Populates file rename dialog entry with the existing name of the file or folder.

## 0.3.3 - 2026-01-29

### Changed

- Rebrands the application
- Changes About dialog contents

## 0.3.2 - 2026-01-24

### Added

- Splitter between the favorites pane and the file browser pane.

## 0.3.1 - 2026-01-23

### Fixed

- Git Tracker Issue #1 - Titlebar Update

## 0.2.1 - 2026-01-23

### Fixed

- Fixes favoriting file bug

## 0.2.0 - 2026-01-21

### Changed

- Allows favoriting of files not only folders

## 0.1.13 - 2026-01-21

### Changed

- Updates the versioning number to be conformant with semantic versioning

## 0.1.7 - 2026-01-17

### Changed

- Default support for a wider range of file types.
  Non-previewable file hiding removed.

## 0.1.6 2026-01-16

### Changed

- Support for external drag and drop of file previewing

## 0.1.5 - 2026-01-15

### Changed

- Allow favorites to be manually rearranged via drag and drop

## 0.1.4 - 2026-01-14

### Changed

- Ability to hide non-previewable files

## 0.1.3 - 2026-01-14

### Changed

- Updated about dialog to include instructions for deleting a favorite and opening a file

## 0.1.2

### Changed

- Added ability to delete a favorite

## 0.1.1 - 2026-01-11

- Initial release