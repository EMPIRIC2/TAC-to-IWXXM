Thank you for downloading your local copy of the IWXXM-US v3.0
schema files.

To aid in performing fast schema validation of XML documents from the
United States, you may wish to use the OASIS catalog file,
united-states-catalog.xml, to instruct your validation tool to refer
to your local copy of these schema files.

Using your favorite editor, open the catalog file, identify and
uncomment the proper element to use based on the computer's operating
system. Change the LOCAL_PARENT_DIRECTORY_PATH string to match the
directory where the ZIP (or the TGZ) file was unpacked, then save the
file.

OR, if you already have a OASIS catalog file that you use for XML
validation, you can simply add the relevant line to it.

By using this catalog file with your validation tool, it will then
replace any references to 'https://nws.weather.gov/schemas' inside the
XML documents with the LOCAL_PARENT_DIRECTORY_PATH string instead of
attempting to download the schema file(s) from the Internet. Your
local copy of these schema files will be read instead, resulting in
much faster XML validation. The XML document remains unchanged after
validation.
