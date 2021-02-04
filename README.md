# toolshed

![Python 3][python-badge]
[![MIT licensed][mit-badge]][mit-link]

Python-based tools for managing data backups


## Tools in the shed

### Bucket

Database backup tool to create structure and data files for each table in each database. Supports optionally encrypting the backup with GPG.

*Currently only supports MySQL.*


### Wheelbarrow

Plone backup tool that handles creating backup copies of both the `Data.fs` and the blob storage files.

*Tested with Plone 4.x and 5.x.*


### Shears

File pruning tool that supports limiting the number of backups in a single folder or in a daily, weekly, monthly, yearly hierarchy.



## License

[MIT][mit-link]


## Author

Created by Paul Rentschler in 2018.


[mit-badge]: https://img.shields.io/badge/license-MIT-blue.svg
[mit-link]: https://github.com/paulrentschler/toolshed/blob/master/LICENSE
[python-badge]: https://img.shields.io/badge/python-3.x-blue
