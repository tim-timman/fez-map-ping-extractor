# Fez Map Ping Extractor

Extracts ones (chime with ping) and zeros (chime without ping) from an audio recording of the Fez map.


## How to use

Requires python 3 (only tested with 3.9)

1. Create a python environment  
   ```sh
   python3.9 -m venv --upgrade-deps venv
   ```
2. Activate the environment  
   ```sh
   source venv/bin/activate      # linux/mac
   source venv/Scripts/Activate  # Windows
   ```
3. Install dependencies
   ```sh
   pip install -r requirements
   ```
4. Run it
   ```sh
   python map-ping-extractor.py <path-to-file>
   ```
   > *See usage*
   > ```
   > $ python map-ping-extractor.py --help
   > usage: map-ping-extractor.py [-h] [--visualize] [--offset OFFSET] [--duration DURATION] [--background BACKGROUND] [--partition PARTITION]
   >                              file
   >
   > positional arguments:
   >   file                  audio file of map ping to analyze
   >
   > optional arguments:
   >   -h, --help            show this help message and exit
   >   --visualize           show the plot (WARNING! Slow for big files)
   >   --offset OFFSET       offset in seconds into the file to start parsing
   >   --duration DURATION   for how many seconds to parse
   >   --background BACKGROUND
   >                         manually set the background threshold value above where peaks should be found (DEFAULT: determined automatically)
   >   --partition PARTITION
   >                         manually set the partition value threshold to separate ping and chime peaks (DEFAULT: determined automatically)
   > ```
