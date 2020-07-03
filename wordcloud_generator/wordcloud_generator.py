"""
Python Script to create a wordcloud from a file provided.
Comes with:
 - giraffe.png
 - heart.png
 - Love :-)
"""

import argparse
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
import re
from pathlib import Path


#############################
# Setup Command-line Options
#############################

parser = argparse.ArgumentParser(
	description="Generates a WordCloud from the words in a provided file\n"\
		"You must specify a file using '-f' or '--file' unless you're using a debug option",
	formatter_class=argparse.RawTextHelpFormatter
)

# Required Parameters

norm_or_debug = parser.add_mutually_exclusive_group()

norm_or_debug.add_argument("-f", "--file", type=str, help="Specify a file to create a wordcloud from")

# File Types

file_type_top_group = parser.add_argument_group(
	"File Type Options"
)
file_type_group = file_type_top_group.add_mutually_exclusive_group()
file_type_group.add_argument("-w", "--whatsapp", help="Specified file is a Whatsapp export (default)", action="store_const", dest="file_type", const="whatsapp", default="whatsapp")
file_type_group.add_argument("-c", "--csv", help="Specified file is a CSV", action="store_const", dest="file_type", const="csv")
parser.set_defaults(file_type="whatsapp")

# WordCloud Mask

mask_top_group = parser.add_argument_group(
	"WordCloud Mask Options"
)
mask_group = mask_top_group.add_mutually_exclusive_group()
mask_group.add_argument("-m", "--mask", help="Specify a custom mask (image) for the Word Cloud", dest="mask")
mask_group.add_argument("--heart", help="Use built-in heart mark (default)", action="store_const", dest="mask", const="heart.png", default="heart.png")
mask_group.add_argument("--giraffe", help="Use built-in giraffe mask", action="store_const", dest="mask", const="giraffe.png")
parser.set_defaults(mask="heart.png")

# Colours

colour_top_group = parser.add_argument_group(
	"WordCloud Colour Options"
)
colour_group = colour_top_group.add_mutually_exclusive_group()
colour_group.add_argument("-p", "--pallet", help="Use specified matplotlib colour pallet\nExamples: PuRd, GnBu, YlOrBr, hsv, magma", dest="colour")
colour_group.add_argument("--magma", help="Use the magma colourmap", action="store_const", dest="colour", const="magma")
colour_group.add_argument("--purd", help="Use a Purple/Red (PuRd) colourmap", action="store_const", dest="colour", const="PuRd")
colour_group.add_argument("--gnbu", help="Use a Green/Blue (GnBu) colourmap (default)", action="store_const", dest="colour", const="GnBu", default="gnbu")
colour_group.add_argument("--multicolour", help="Use ALL THE COLOURS", action="store_const", dest="colour", const="hsv")
colour_group.add_argument("--infer-colour", help="Infer the colour from the mask file", action="store_const", dest="colour", const="infer")
parser.set_defaults(colour="GnBu")

# Other Optional Parameters

other_config = parser.add_argument_group(
	"Optional Config"
)

other_config.add_argument("-i", "--ignore", help="Specify a list of characters to be removed from words.\nBy default these are .,!?;:\nAny words containing other non alphanumeric characters will be ignored from the wordcloud", default=".,!?;:")
other_config.add_argument("-v", "--verbose", help="Give verbose output", action="store_true")
other_config.add_argument("-o", "--output", help="Output directory. Default is ./wcg_output")



# Debug Options
debug_group = parser.add_argument_group(
	"Debug Options",
	"These Options will perform the specified debug option, and then exit without creating a WordCloud\n"\
		"You do not need to specify a file when using these options"
	)
debug_group.add_argument("--colourmap", help="Prints a list of available colourmaps", action="store_true")
debug_group.add_argument("--display-mask", help="Displays how we can see the provided WordCloud map", action="store_true")

cmd_args = parser.parse_args()


#############################
# Internal Functions
#############################


def v_print(*args, **kwargs):
	if cmd_args.verbose:
		print(*args, **kwargs)


#############################
# Main Class
#############################


class WordCloudGenerator:
	"""
	Principal class to generate a WordCloud
	"""

	def __init__(self, cmd_options, debug=False):
		
		# Setup some internal variables

		self.file_data = list()
		self.word_data = dict()
		self.working_dir = Path.cwd()
		self.script_dir = Path(__file__).parent
		self.mask_array = None

		# Parse variables out

		if not debug:
			self.input_file = self._find_file(cmd_options.file)
		self.file_type = cmd_options.file_type
		self.mask = self._find_file(cmd_options.mask)
		self.colour = cmd_options.colour
		self.illegal_chars = cmd_options.ignore
		self.output = Path(cmd_options.output) if cmd_options.output else self.script_dir / "wcg_output/"

		# Run checks

		if not debug:
			self._check_file()
		self._check_mask()
		self._check_colour()

		if not self.output.is_dir():
			self.output.mkdir()

	def _find_file(self, filename):
		"""
		Generic function to find a given file, and return the full path.
		This looks for the provided path, in the working directory, and in the script directory
		"""
		# Look for the file as specified
		if Path(filename).is_file():
			return Path(filename)

		# Look for file in the working directory
		if Path(self.working_dir / filename).is_file():
			return Path(self.working_dir / filename)
		
		# Look for file in the script directory
		if Path(self.script_dir / filename).is_file():
			return Path(self.script_dir / filename)
		
		# Else raise exception
		raise FileNotFoundError(f"The file ({filename}) cannot be found.")

	def _check_file(self):
		"""
		Checks the self.input_file to make sure that it's valid
		"""

		# Try to open the file, and read any data
		
		if self.file_type == "csv":
			v_print("Reading in file as a CSV")
			self.file_data = pd.read_csv(self.input_file)
			rows, columns = self.file_data.shape
			v_print(f"This CSV has {rows} row(s) and {columns} column(s)")

			if columns > 3:
				raise Exception("CSV appears to have more than 3 columns. WordCloudGenerator cannot parse this file")
			if rows < 1:
				raise Exception("CSV appears to have no rows. WordCloudGenerator cannot parse this file")
		
		elif self.file_type == "whatsapp":
			v_print("Reading in file as a Whatsapp export")
			self.file_data = [line.rstrip('\n') for line in open(self.input_file, encoding="utf8")]
			v_print(f"This WhatsApp export has {len(self.file_data)} line(s) of data in it")
	  
		else:
			raise Exception("Specified file is of unknown type")

		v_print()
		return True

	def _check_mask(self):
		try:
			self.mask_array = np.array(Image.open(self.mask))
		except:
			raise Exception(f"Unable to parse the provided mask ({self.mask}) into a numpy array")

	def _check_colour(self):
		if self.colour == "infer":
			pass
		elif self.colour not in plt.colormaps():
			raise Exception(f"The colourmap provided ({self.colour}) does not exist")
	
	def _parse_csv(self):
		"""
		Parse self.input_file as a CSV.
		We're going to assume that this CSV is 1, 2, or 3 columns:
		1 - Just words from a single person
		2 - Name and message from 1 or more people
		3 - Name, message, and timestamp from 1 or more people

		To parse the columns, we're going to assume that:
		- There will be fewer than 256 people (seriously, why would a group have more than that), and their name will follow a regex pattern (below)
		- Timestamps are going to follow a specific regex pattern (below)
		- The other column will be the messages
		"""
		print("Parsing data from CSV...")

		re_timestamp = re.compile("^[0-9TZ:. -+]{4,25}$")
		re_name = re.compile("^[A-Za-z0-9 -]{1,30}$")

		# We're going to iterate over the df (csv) and try to figure out which column is which
		
		name_col = None
		time_col = None
		message_col = None

		v_print()
		v_print("Parsing columns to determine what is what...")
		col_list = list(self.file_data.columns)
		for col in col_list:
			v_print(f"\tChecking column '{col}'")

			# Check for timestamp
			if not time_col:
				v_print(f"\t\tTimestamps?", end='')
				for index, row in self.file_data.iterrows():
					if not re_timestamp.match(row[col]):
						v_print(f" ==> No - Column '{col}' doesn't appear to be a timestamp. Failed on row {index}")
						break
					if index == len(self.file_data) - 1:
						v_print(f" ==> Yes! - Column '{col}' appears to be a timestamp")
						time_col = col
				if time_col:
					continue
			
			# Check for names
			if not name_col:
				v_print(f"\t\tNames?", end='')	  
				for index, row in self.file_data.iterrows():
					if not re_name.match(row[col]):
						v_print(f" ==> No - Column '{col}' doesn't appear to contain names. Failed on row {index}")
						break
					if index == len(self.file_data) - 1:
						if len(self.file_data[col].unique()) > 255:
							v_print(f" ==> No - Column '{col}' has too many unique values ({len(self.file_data[col].unique())})")
						else:
							v_print(f" ==> Yes! - Column '{col}' appears to contain {len(self.file_data[col].unique())} name(s).")
							name_col = col
				if name_col:
					continue
			
			# Assume the one left is the message column
			if not message_col:
				v_print(f"\t\t...which means that column '{col}' must contain the messages")
				message_col = col
		
		v_print()
		# For each name, we're going to create a word list in the self.word_data

		names = list(self.file_data[name_col].unique())
		print("Parsing data for each of the following people:")

		for name in names:
			print(f"\t {name}", end='')
			self.word_data[name] = self._extract_words(self.file_data.loc[self.file_data[name_col] == name][message_col])

			print(f" -> {len(self.word_data[name])} words extracted") 


	def _parse_whatsapp(self):
		"""
		Parse self.input file as a WhatsApp export file
		These files are formatted as follows:

		17/01/2018, 19:15 - Firstname 1: This is my first message to person Two
		17/01/2018, 19:16 - Firstname 1: This is another message that happened in a different minute
		17/01/2018, 19:21 - Firstname Surname 2: This is the second person's reply...
		This is the second person's second reply, that happened in the same minute as the last message 🙂
		"""
		
		print("Parsing data from WhatsApp Export...")

		# Regex to parse a newline. Groups are (Person, Message)
		re_new_line = re.compile("^[0-9]{2}/[0-9]{2}/[0-9]{4}, [0-9]{2}:[0-9]{2} - ([A-Za-z0-9 -]{1,30}): (.+)$")
		person_data = dict()

		# We have to do weird stuff with WhatsApp data
		# If a line conforms to the regex above, we can parse the person out, and append the line to their list
		# If not, we need to remember who spoke last, and append the line to theirs

		for line in self.file_data:
			regex_match = re_new_line.search(line)

			try:
				# See if we hit the regex
				regex_match.string
			except AttributeError:
				# Case -> Regex doesn't hit - Line Continuation
				message = line
			else:
				# Case -> Regex hits - New Line
				reg_captures = re_new_line.match(line)
				person = reg_captures.group(1)
				message = reg_captures.group(2)

			# Now we have the person and message string, we can add these to the person_data dict

			try:
				person_data[person].append(message)
			except KeyError:
				person_data[person] = [message]
		
		print("Parsing data for the following people:")

		for name, message_list in person_data.items():
			print(f"\t {name}", end='')
			self.word_data[name] = self._extract_words(message_list)
			print(f" -> {len(self.word_data[name])} words extracted")
		


	def _extract_words(self, message_list):
		"""
		Returns a dict of word frequency from the provided list of messages
		"""
		unparsed_word_list = list()

		# Extract all of the words

		for message in message_list:
			unparsed_word_list.extend(message.split())

		# Parse the unparsed list
		word_freq = dict()
		
		for word in unparsed_word_list:
			word = word.upper()

			# Throw away illegal characters
			for char in self.illegal_chars:
				word = word.replace(char, '')
			
			# Use this word if it's an alphanumeric word
			re_alphanumeric = re.compile("^[A-Z0-9]+$")
			if re_alphanumeric.match(word):
				try:
					word_freq[word] += 1
				except KeyError:
					word_freq[word] = 1

		return word_freq
	
	def generate_cloud(self):
		"""
		Generates a WordCloud based on the provided file type
		"""

		if self.file_type == "csv":
			self._parse_csv()
		elif self.file_type == "whatsapp":
			self._parse_whatsapp()

		print()
		if len(self.word_data) > 0:
			print(f"Generating {len(self.word_data)} WordCloud(s)")
			for name, word_list in self.word_data.items():
				print(f"\tGenerating WordCloud for {name}...", end='')
				if self._generate_cloud_from_list(name, word_list):
					print(" Complete")
				else:
					print(" Failed. An error ocurred while creating this WordCloud")
			
			print()
			print("Done. Your WordClouds can be found in the following directory:")
			print(self.output)
		else:
			print("Nothing to do")
		return True

	def _generate_cloud_from_list(self, name, word_list):
		"""
		Generates a WordCloud from a word_list
		"""
		plt.figure(figsize=[25,25], dpi=80)
		plt.axis('off')
		
		if self.colour == "infer":
			custom_colours = ImageColorGenerator(self.mask_array)
			cloud = WordCloud(max_words=2000, mask=self.mask_array).fit_words(word_list)
			plt.imshow(cloud.recolor(color_func=custom_colours), interpolation="bilinear")
		else:
			cloud = WordCloud(max_words=2000, mask=self.mask_array, colormap=self.colour)
			cloud.fit_words(word_list)
			plt.imshow(cloud, interpolation="bilinear")
		
		colour_name = "custom_colour" if self.colour == "infer" else self.colour
		output_file = self.output / f"wordcloud_{name}_{self.mask.stem}_{colour_name}.png"
		plt.savefig(output_file, dpi=150, transparent=True)
		
		return True

	def display_mask(self):
		"""
		Displays how matplotlib will see the mask provided
		"""
		mask = np.array(Image.open(self.mask))
		mask_image = Image.fromarray(mask, 'RGB')
		mask_image.show()



#############################
# Running Code
#############################

wcg_art = r"""
__          __           _  _____ _                 _    _____                           _             
\ \        / /          | |/ ____| |               | |  / ____|                         | |            
 \ \  /\  / /__  _ __ __| | |    | | ___  _   _  __| | | |  __  ___ _ __   ___ _ __ __ _| |_ ___  _ __ 
  \ \/  \/ / _ \| '__/ _` | |    | |/ _ \| | | |/ _` | | | |_ |/ _ \ '_ \ / _ \ '__/ _` | __/ _ \| '__|
   \  /\  / (_) | | | (_| | |____| | (_) | |_| | (_| | | |__| |  __/ | | |  __/ | | (_| | || (_) | |   
    \/  \/ \___/|_|  \__,_|\_____|_|\___/ \__,_|\__,_|  \_____|\___|_| |_|\___|_|  \__,_|\__\___/|_|   
																									   
"""

if __name__ == "__main__":

	print(wcg_art)

	# Check for either Debug options, or run mode

	# # Normal -> Standard Run mode
	if cmd_args.file:
		v_print("------- Verbose Output On -------", end="\n\n")

		v_print("Running with the following parameters:")
		v_print()
		v_print(f"File:        {cmd_args.file}")
		v_print(f"File Type:   {cmd_args.file_type}")
		v_print(f"Mask:        {cmd_args.mask}")
		v_print(f"Colours:     {cmd_args.colour}")
		v_print(f"Ignored:     {cmd_args.ignore}")
		v_print()

		wc = WordCloudGenerator(cmd_args)
		wc.generate_cloud()

	# # Debug -> Display Colourmaps
	elif cmd_args.colourmap:
		print("Debug Option - List of available colourmap options. These can be specifiied with the -p option:")
		print()
		for colour in plt.colormaps():
			print(f" - {colour}")

	# # Debug -> Display Mask
	elif cmd_args.display_mask:
		print("Debug Option - Displaying the specified mask")
		debug = WordCloudGenerator(cmd_args, debug=True)
		debug.display_mask()

	# # Other -> Nothing specified
	else:
		print("You specified neither a file, nor a debug option.")
		print("For usage help, run again with the '--help' option")

	# Termination

	print("\nWordCloud Generator will now exit")
