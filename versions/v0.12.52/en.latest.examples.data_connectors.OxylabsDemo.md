![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)
# Oxylabs Reader¶
Use Oxylabs Reader to get information from Google Search, Amazon and YouTube. For more information check out the Oxylabs documentation.
In [ ]:
Copied!
```
%pip install llama-index llama-index-readers-oxylabs

```

%pip install llama-index llama-index-readers-oxylabs
In this notebook, we show how Oxylabs readers can be used to collect information from different sources.
Firstly, import one of the Oxylabs readers.
Currently available readers are:
  * OxylabsAmazonSearchReader
  * OxylabsAmazonPricingReader
  * OxylabsAmazonProductReader
  * OxylabsAmazonSellersReader
  * OxylabsAmazonBestsellersReader
  * OxylabsAmazonReviewsReader
  * OxylabsGoogleSearchReader
  * OxylabsGoogleAdsReader
  * OxylabsYoutubeTranscriptReader


In [ ]:
Copied!
```
import os
from llama_index.readers.oxylabs import OxylabsGoogleSearchReader

```

import os from llama_index.readers.oxylabs import OxylabsGoogleSearchReader
Instantiate the reader with your username and password.
In [ ]:
Copied!
```
oxylabs_username = os.environ.get("OXYLABS_USERNAME")
oxylabs_password = os.environ.get("OXYLABS_PASSWORD")

google_search_reader = OxylabsGoogleSearchReader(
    oxylabs_username, oxylabs_password
)

```

oxylabs_username = os.environ.get("OXYLABS_USERNAME") oxylabs_password = os.environ.get("OXYLABS_PASSWORD") google_search_reader = OxylabsGoogleSearchReader( oxylabs_username, oxylabs_password )
Prepare parameters. This example will load the Google Search results for the 'iPhone 16' query with the 'Berlin, Germany' location.
Check out the documentation for more examples.
In [ ]:
Copied!
```
results = google_search_reader.load_data(
    {"query": "Iphone 16", "parse": True, "geo_location": "Berlin, Germany"}
)

print(results[0].text)

```

results = google_search_reader.load_data( {"query": "Iphone 16", "parse": True, "geo_location": "Berlin, Germany"} ) print(results[0].text)
```
  ORGANIC RESULTS ITEMS:
    ORGANIC-ITEM-1:
    POS: 1
    URL: https://www.apple.com/de/iphone-16/
    DESC: Dieses Design verdient ein langes Leben. Das iPhone 16 hat ein Gehäuse aus Aluminium in Raumfahrt-Qualität und durchgefärbtes Glas auf der Rückseite, das extrem ...
    TITLE: iPhone 16 und iPhone 16 Plus - Apple (DE)
    SITELINKS:
      SITELINKS:
      EXPANDED ITEMS:
        EXPANDED-ITEM-1:
        URL: https://www.apple.com/de/shop/buy-iphone/iphone-16-pro
        TITLE: iPhone 16 Pro kaufen
        EXPANDED-ITEM-2:
        URL: https://www.apple.com/de/iphone-16-pro/
        TITLE: iPhone 16 Pro
  ...

```

## More examples¶
### Amazon Product¶
In [ ]:
Copied!
```
from llama_index.readers.oxylabs import OxylabsAmazonProductReader


amazon_product_reader = OxylabsAmazonProductReader(
    oxylabs_username, oxylabs_password
)

results = amazon_product_reader.load_data(
    {
        "domain": "com",
        "query": "B08D9N7RJ4",
        "parse": True,
        "context": [{"key": "autoselect_variant", "value": True}],
    }
)

print(results[0].text)

```

from llama_index.readers.oxylabs import OxylabsAmazonProductReader amazon_product_reader = OxylabsAmazonProductReader( oxylabs_username, oxylabs_password ) results = amazon_product_reader.load_data( { "domain": "com", "query": "B08D9N7RJ4", "parse": True, "context": [{"key": "autoselect_variant", "value": True}], } ) print(results[0].text)
```
# Products
- Item 1:
  ## url
    https://www.amazon.com/dp/B08D9N7RJ4?th=1&psc=1

  ## asin
    B08D9N7RJ4

  ## page
    1

  ## brand
    Philips Hue
...

```

### YouTube Transcript¶
In [ ]:
Copied!
```
from llama_index.readers.oxylabs import OxylabsYoutubeTranscriptReader


youtube_transcript_reader = OxylabsYoutubeTranscriptReader(
    oxylabs_username, oxylabs_password
)

results = youtube_transcript_reader.load_data(
    {
        "query": "SLoqvcnwwN4",
        "context": [
            {"key": "language_code", "value": "en"},
            {"key": "transcript_origin", "value": "uploader_provided"},
        ],
    }
)

print(results[0].text)

```

from llama_index.readers.oxylabs import OxylabsYoutubeTranscriptReader youtube_transcript_reader = OxylabsYoutubeTranscriptReader( oxylabs_username, oxylabs_password ) results = youtube_transcript_reader.load_data( { "query": "SLoqvcnwwN4", "context": [ {"key": "language_code", "value": "en"}, {"key": "transcript_origin", "value": "uploader_provided"}, ], } ) print(results[0].text)
```
# YouTube video transcripts
- Item 1:
  - Item 1:
    ### transcriptSectionHeaderRenderer
      #### startMs
        0

      #### endMs
        25000

      #### accessibility
        ##### accessibilityData
          ###### label
            Introduction

      #### trackingParams
        CAIQ8bsCIhMIntXqp4f6jAMVlSqzAB2-DSWc

      #### enableTappableTranscriptHeader
        True

      #### sectionHeader
        ##### sectionHeaderViewModel
          ###### headline
            ###### content
              Introduction
  ...

```

