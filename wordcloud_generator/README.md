# WordCloud Generator

A little python script to generate a Wordcloud from a provided WhatsApp message file, or a .csv.  
Uses the **amueller** [word_cloud library](https://github.com/amueller/word_cloud).

## Usage

Run WordCloud Generator by invoking it on the command-line:

> python wordcloud_generator.py -f whatsapp_file.txt

Your input file can either be WhatsApp format, or a .csv:
> python wordcloud_generator.py -f whatsapp_file.txt -w  
> python wordcloud_generator.py -f chat.csv -c

You can use either of the built-in images as the mask for your Wordcloud, or specify your own
> python wordcloud_generator.py -f whatsapp_file.txt --heart  
> python wordcloud_generator.py -f whatsapp_file.txt --giraffe  
> python wordcloud_generator.py -f whatsapp_file.txt -m my_mask.png

You can specify any colour within the matplotlib colour pallet with "-p colour", or use a built-in colour pallet, for example:
> python wordcloud_generator.py -f whatsapp_file.txt --magma  
> python wordcloud_generator.py -f whatsapp_file.txt --multicolour  
> python wordcloud_generator.py -f whatsapp_file.txt -p GnBu

If your mark is in colour and you'd like to keep those colours, we can infer the colour (this works really well on the giraffe mask):
> python wordcloud_generator.py -f whatsapp_file.txt --giraffe --infer-colour

To ignore certain characters from your Wordcloud, pass an ignore list:
> python wordcloud_generator.py -f whatsapp_file.txt -i .,!?^%

By default, your images will output into "./wcg_output" but you can specify the output directory yourself:
> python wordcloud_generator.py -f whatsapp_file.txt -o /home/wcg/wordclouds  
> python wordcloud_generator.py -f whatsapp_file.txt -o C:\Users\wcg\Documents\wordclouds

There are some debug options available:
> python wordcloud_generator.py --colourmap (lists all available colourmaps)  
> python wordcloud_generator.py -m my_mask.png --display-masks (previews how we see your custom mask)

To get more help while using this, pass the --help commmand:
> python wordcloud_generator.py --help

## Dependencies
- [wordcloud](https://github.com/amueller/word_cloud)
- [pandas](https://github.com/pandas-dev/pandas)
- [numpy](https://github.com/numpy/numpy) (comes with pandas and wordcloud)
- [matplotlib](https://github.com/matplotlib/matplotlib) (comes with wordcloud)

You can install these dependenies with:
> python -m pip install wordcloud pandas numpy matplotlib
