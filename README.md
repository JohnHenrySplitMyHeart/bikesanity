# BikeSanity Cycle Journal Exporter for CrazyGuyOnABike

### What is this?

In this repository is the complete code needed to download, extract, interpret, and export - in an attractive, completely new and _mobile friendly_ HTML format - bicycle touring journals available in the popular [crazyguyonabike.com](https://www.crazyguyonabike.com) (CGOAB) website.

You can use it download and create backups of your journals, to interpret them into a form where the content is easier to extract, and to re-format them in various formats readable offline.

All the authored content in journals will be retrieved, including all pages, text, images and maps. "Social" content such as guestbooks will not be retrieved.

For technical users, it also populates an object model of all cycle journals. You can write your own Python programs, and linking to this library get hold of `Journal` objects containing sensibly structured content for you to work on as you wish.

### Can I see a sample of an extracted journal?

Sure! The `samples/html` folder contains a sample of the converted journal HTML format, generated using placeholder data. This shows off the responsive layout, cleaner design, and fully working map embedding. You can browse that sample live at [https://www.bikejournalbackup.com/journals/sample/index.html](https://www.bikejournalbackup.com/journals/sample/index.html).

All images used in the sample are in the public domain and freely licensed from [pexels](https://www.pexels.com/).

### How can I use this tool?
 
This is a command line tool, and source code written in Python 3.6, to perform journal extraction.

If you are comfortable using command line tools and have Python on your system, you can install this module and use it directly.

Otherwise you may be better off using the user-friendly graphical tool (coming soon). That is built on top of this library and so can perform the same actions, but will be easier for non-technical users.

### Who can use it?

Anyone. All code is free and open source, and provided as a service to the cycle touring community. 

The code is licensed under the permissive Apache 2.0 license. Please feel free to fork this code, or use it for your own development.


### Installing this module

This is standard Python package, and you can install it from PyPi or directly using `pip`

    pip install bikesanity 

or, after cloning/downloading the repository, in the base directory
    
    pip install .

The module is implemented in pure Python, with a few dependencies which will be automatically installed.

After installation, the `bikesanity-run` script will be made available on your path. Run

    bikesanity-run --help
    
to see options.

### Quick Start

The three simple commands will download, interpret, and re-output a journal in new HTML

    bikesanity-run download <http://www.crazyguyonabike.com/doc/JournalNameHere>
    bikesanity-run process <12345>
    bikesanity-run publish <12345>

Replace `<>` values with a link to the journal you want to download, and its ID (which will be shown to you upon download). The your re-formatted journal will be available in `CycleSanityJournals/processed/12345/html/index.html`!


### Retrieving and interpreting journal content using the script 

The `bikesanity-run` script can perform four different operations:

1. Download of a complete journal, as is, from crazyguyonabike.com
2. Interpretation ("processing") of a _downloaded_ journal to extract  all the content into an understandable internal (object) model.
3. Interpretation of an _exported_ journal (i.e. one formally exported using the tool provided by CGOAB) to extract all the content
4. Publishing of a processed journal to create new, clean HTML content including all images, maps, and structure locally browseable.

By default all journals will be downloaded and processed into a folder created in your home directory (`/home/<usr>/CycleSanityJournals` on mac/linux, `c:\Users\<usr\CycleSanityJournals` on Windows). You can change this path using the options below.

#### Downloading journals

Download a journal by using the `download` argument and providing a URL to the journal front page. This can be a permalink like `http://www.crazyguyonabike.com/doc/JournalNameHere`.

    bikesanity-run download http://www.crazyguyonabike.com/doc/JournalNameHere
    
Because of the slow rate of retrieval from CGOAB, this can take a few minutes or longer for very large journals. The default download path will be `CycleSanityJournals/downloads/<journal_id>`. You can change it with the options below:

- `--location` changes the location to download to.
- `--from-page` picks up the download from a provided page number, e.g. `--from-page 8`. This is useful for picking up downloads that failed, e.g. in the middle.
- `--do-process` also performs an interpreting processing run once the download has completed (see below)
- `--no-local-readability-postprocessing` turns off post-processing to make journals locally readable and navigable (advanced)

#### Processing journals

Downloaded or exported journals can be interpreted using the `process` or `process-exported` arguments respectively. You should provide the _journal id_, which will be the number attributed to the downloaded folder, e.g. 12345.

    bikesanity-run process 12345

By default, the processor expects downloaded journals to be in the `CycleSanityJournals/downloads/<journal_id>` directory, and exported journals to be in `CycleSanityJournals/exported/<journal_id>`. It will output processed journals on the path `CycleSanityJournals/processed/<journal_id>`.

Options:
- `--input_location` changes the location to take downloaded/exported input from
- `--out_location` changes the location to send processed output to

Following processing, a complete object model of the journal will be created and saved in as a serialized Python pickle as `journal.pickle` - for technical users, you may wish to load and inspect this. All resources (images and maps) will be copied to the new `processed/resources` location.

#### Locally publishing to HTML

Currently it possible to publish processed journals to attractive and clean HTML that can be fully-functionally browsed on the local machine, including dynamic maps. Publish any processed journal to HTML using the `publish` argument and providing the same _journal id_:

    bikesanity-run publish <12345>

By default, HTML is output inside the processed directory, at `CycleSanityJournals/processed/<journal_id>/html` - open `index.html` to browse the journal index.

Options:
- `--input_location` changes the location to take processed input from
- `--out_location` changes the location to send HTML output to. Note links to resources may break if your change this.

HTML is generated by populating templates. These are available in `resources/templates` if you would like to adjust the exact appearance of the output. Publication to PDF and EPUB is work in progress - watch this space!

### Why is this necessary?

CGOAB has for twenty years been a fantastic resource. What has made it so good has been the contributions of the wonderful bike touring community. It contains a wealth of material primarily in the form of thousands of journals describing bicycle tours.

However, in recent years the site has seen significant fall in user activity. Since 2016, the rate of journal submission has roughly halved. A sometimes toxic environment on the site forum has driven away many users.
 
The site is run and maintained by one person. It has become clear that the understandable work involved in running the site has become a significant burden, financial and otherwise, on the administrator. 

Nobody except the owner can administrate the site, or know how its bespoke and now very old internals work. The site is now extremely dated in appearance and operation.
 
Because of the factors above, there is a significant risk that CGOAB is vulnerable to eventual outage. This means there is a serious consideration that years of work and thousands of touring journals may be lost forever. BikeSanity allows these journals to be retrieved for posterity and never lost.

### How do we know it works?

The interpreter has been successfully tested against >10000 journals.

### What difficulties are there in retrieving journal content?

To the great credit of CGOAB's administrator, two factors make retrieving journal content easier than it could be:

1. All content is owned purely by their authors. The administrator does not own any of the journal content (that he has not authored).
2. CGOAB provides an "export" function that can allow journals to be downloaded as-is from the site.

**However**, even after export, the content remains in CGOAB's peculiar HTML format. This is highly non-standard and often faulty (see technical details below) and very laborious to extract content from manually.

The administrator of CGOAB is extremely resistant to any attempts to liberate journal content from this old and unworkable format. To make it reliably readable into the future, a robust parser is needed. This library attempts to provide that facility.

### What technical deficiencies are there in CGOAB journal format?

Unfortunately, it's clear that there are serious technical deficiencies in the CGOAB site and platform which are actively causing problems with maintaining and modernising the site, and are a risk factor for its long-term stability.

The front end code has serious problems:
- No CSS is used across the site *whatsoever*. All style is baked directly into HTML, an extremely bad practice. This is one reason why the antiquated visual style of the site has never changed, and would be very difficult to change.
- JavaScript is baked in HTML across the site, and is repeated in every single page.
- All the HTML uses nonstandard markup and is a terrible mess. Cases of tags are mixed indiscriminately, e.g. `<B>` vs `<b>`. HTML tags are not closed properly, and sometimes are nested recursively, like the `DD` tags.

These are very basic errors that have a direct impact on the difficulty for the administrator to maintain and update the site. A case in point is responsive layour for mobile devices, which has been requested for many years yet but is still not supported. Google terminating their free mapping API caused a major panic and months to resolve.

These problems raise serious worries about the robustness of the server code. At the very least, it is likely to be impossible to work with for anyone other than their creator, who has developed the entire site in isolation from modern coding practices.

### Do you have any relationship with any other bicycle touring resources?

No, none whatsoever. This tool has been provided completely independently and _pro bono_ for the benefit of the cycle touring community. If you plan to make copies or republish material retrieved by this tool, please ensure that you are, or have permission of, the author.

Absolutely no property of CGOAB is included in this library whatsoever. All code is original, other than third-party libraries which have appropriate open-source licenses attached.

