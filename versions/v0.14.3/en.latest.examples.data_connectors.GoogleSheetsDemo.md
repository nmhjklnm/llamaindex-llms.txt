#  **Google Sheets Reader**¶
Demonstrates Google Sheets Reader in LlamaIndex
  * Make Sure you have token.json or credentials.json file in the Environment, More on that here


In [ ]:
Copied!
```
from llama_index.readers.google import GoogleSheetsReader

```

from llama_index.readers.google import GoogleSheetsReader
Load Sheets as a List of Pandas Dataframe
In [ ]:
Copied!
```
list_of_sheets = ["1ZF5iIeLLqROHbHsb1vOeRaLWKIgLU7rDDTSOZaqjpk0"]
sheets = GoogleSheetsReader()
dataframes = sheets.load_data_in_pandas(list_of_sheets)

```

list_of_sheets = ["1ZF5iIeLLqROHbHsb1vOeRaLWKIgLU7rDDTSOZaqjpk0"] sheets = GoogleSheetsReader() dataframes = sheets.load_data_in_pandas(list_of_sheets)
In [ ]:
Copied!
```
dataframes[0]

```

dataframes[0]
Out[ ]:
| spotify_id | name | artists | daily_rank | daily_movement | weekly_movement | country | snapshot_date | popularity | is_explicit | ... | key | loudness | mode | speechiness | acousticness | instrumentalness | liveness | valence | tempo | time_signature  
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---  
0 | 2HafqoJbgXdtjwCOvNEF14 | Si No Estás | iñigo quintero | 1 | 0 | 3 |  | 2023-10-27 | 97 | FALSE | ... | 5 | -8.72 | 1 | 0.0285 | 0.827 | 0 | 0.138 | 0.524 | 98.224 | 4  
1 | 7x9aauaA9cu6tyfpHnqDLo | Seven (feat. Latto) (Explicit Ver.) | Jung Kook, Latto | 2 | 4 | 0 |  | 2023-10-27 | 97 | TRUE | ... | 11 | -4.107 | 1 | 0.0434 | 0.311 | 0 | 0.0815 | 0.89 | 124.997 | 4  
2 | 3rUGC1vUpkDG9CZFHMur1t | greedy | Tate McRae | 3 | -1 | 2 |  | 2023-10-27 | 99 | TRUE | ... | 6 | -3.18 | 0 | 0.0319 | 0.256 | 0 | 0.114 | 0.844 | 111.018 | 1  
3 | 4MjDJD8cW7iVeWInc2Bdyj | MONACO | Bad Bunny | 4 | -1 | -3 |  | 2023-10-27 | 96 | TRUE | ... | 4 | -5.009 | 0 | 0.068 | 0.15 | 0.000402 | 0.58 | 0.13 | 139.056 | 4  
4 | 7iQXYTyuG13aoeHxGG28Nh | PERRO NEGRO | Bad Bunny, Feid | 5 | 0 | 1 |  | 2023-10-27 | 94 | TRUE | ... | 5 | -2.248 | 1 | 0.262 | 0.0887 | 2.16E-05 | 0.179 | 0.345 | 96.057 | 4  
... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ... | ...  
36395 | 0AYt6NMyyLd0rLuvr0UkMH | Slime You Out (feat. SZA) | Drake, SZA | 46 | 4 | 0 | AE | 2023-10-18 | 84 | TRUE | ... | 5 | -9.243 | 0 | 0.0502 | 0.508 | 0 | 0.259 | 0.105 | 88.88 | 3  
36396 | 2Gk6fi0dqt91NKvlzGsmm7 | SAY MY GRACE (feat. Travis Scott) | Offset, Travis Scott | 47 | 3 | 0 | AE | 2023-10-18 | 80 | TRUE | ... | 10 | -5.06 | 1 | 0.0452 | 0.0585 | 0 | 0.132 | 0.476 | 121.879 | 4  
36397 | 26b3oVLrRUaaybJulow9kz | People | Libianca | 48 | 2 | 0 | AE | 2023-10-18 | 88 | FALSE | ... | 10 | -7.621 | 0 | 0.0678 | 0.551 | 1.31E-05 | 0.102 | 0.693 | 124.357 | 5  
36398 | 5ydjxBSUIDn26MFzU3asP4 | Rainy Days | V | 49 | 1 | 0 | AE | 2023-10-18 | 88 | FALSE | ... | 9 | -8.016 | 0 | 0.0875 | 0.739 | 0 | 0.148 | 0.282 | 74.828 | 4  
36399 | 59NraMJsLaMCVtwXTSia8i | Prada | cassö, RAYE, D-Block Europe | 50 | 0 | 0 | AE | 2023-10-18 | 94 | TRUE | ... | 8 | -5.804 | 1 | 0.0375 | 0.001 | 1.79E-06 | 0.113 | 0.422 | 141.904 | 4  
36400 rows × 25 columns
Or Load Sheets as a List of Document Objects
In [ ]:
Copied!
```
documents = sheets.load_data(list_of_sheets)

```

documents = sheets.load_data(list_of_sheets)
