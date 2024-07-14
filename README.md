# ADIF log file missing grid locators updater

When working digital modes like FT8, sometimes the ADIF file maintained by the logging software (like WSJT-X for example) is missing some grid locators, because some stations answered to your CQ without sending their locator first, or you contacted them directly without knowing their grid.

These missing grid data in your running log prevents your digital mode software to properly do its job of alerting you when a new grid is available, or when you're trying to contact a grid that you worked already.

To fix this, this Python script updates your software's ADIF log by "filling the blanks" using grid data that you have entered manually afterwards in your own logging software, and exported in another ADIF file.

<br/>
  
## Usage/Examples

When you run the script, it will ask for 3 files :

1. An ADIF log file containing the right grid locators (exported from your logging app, like Cloudlog for example).
2. The original ADIF log file with missing grid locators (from WSJT-X for example), that you want to update.
3. The output ADIF log file, that'll be the same as the original log file but with all missing grid locators fixed.


The script then finds all matching QSOs between log files 1 and 2, and updates the 2nd file (the one that has missing grids) with grid locators from the 1st file.

It also updates the TX power and operator name too, if needed.

All updated QSOs are written to a new log file, and files 1 and 2 are left untouched.
