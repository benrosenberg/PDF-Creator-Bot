import discord, asyncio, logging, os, math, subprocess, json, dotenv
from discord.ext import commands
from discord.ext.commands import Bot

dotenv.load_dotenv()
TOKEN = os.getenv("TOKEN")

description = 'Bot that converts uploaded Markdown files into LaTeX PDF files'

bot = discord.Client()

@bot.event
async def on_ready():
	print('Logged in as: ')
	print(bot.user.name)
	print(bot.user.id)
	print('------------')
	activity = discord.Activity(name = 'for Markdown uploads', type = discord.ActivityType.watching)
	await bot.change_presence(activity=activity)

@bot.event
async def on_message(message):
	if message.author.bot: return
	if message.content[:3].lower() not in ['pdf', 'png']: return
	if message.content[:3].lower() == 'png' and message.content[3:] != '':
		await message.channel.send("PNG uploads should have empty content fields.")
		return
	text_content = message.content[4:]
	if message.attachments == [] and text_content == '':
		await message.channel.send("Either attach a file or use the content field.")
		return
	elif message.attachments == []:
		# read content in as message
		f = open("saved/content.md", "w")
		f.write(text_content)
		f.close()

		pdf_path = pandoc("content")
		## use femto.pw for hosting
		femto_json = json.loads(subprocess.check_output('curl -F "upload=@' + pdf_path + '" https://v2.femto.pw/upload', shell=True))
		femto_url = "https://v2.femto.pw/" + femto_json['data']['short']
		print("femto_url: ", femto_url)
		print('femto_json: ', femto_json)

		preview_path = preview("content")
		preview_file = discord.File(preview_path)

		# create an embed to send things in
		# the thumbnail will be the file link
		# the image will be the preview image
		embed_title = "PDF link"
		embed_desc = "PDF requested by " + message.author.mention
		footer_text = "Comments or concerns? Issues? Contact thief#0001 or go to https://bots.thief.fyi."

		result = os.path.getsize('saved/content.md')
		pdfsize = os.path.getsize(pdf_path)
		pdf_pages = str(subprocess.check_output('qpdf --show-npages ' + pdf_path, shell=True))
		pdf_pages = pdf_pages[2:-3]
		size_text = "Size in bytes of plaintext: " + str(result) + '\nSize in bytes of output: ' + str(pdfsize) + '\nNumber of pages: ' + pdf_pages

		embed = discord.Embed(title = embed_title, description = embed_desc,color=discord.Color.teal(), url = femto_url)
		embed.add_field(name="Document Stats", value = size_text)
		#embed.add_field(name="Bot Info", value="PDF files are hosted at [femto.pw](https://v2.femto.pw)")
		embed.add_field(name="Preview Image", value = 'Below is a low-res preview of your PDF.', inline = False)
		embed.set_image(url="attachment://content.png")
		embed.set_thumbnail(url = message.author.avatar_url_as(size=512))
		# embed.set_author(name = message.author.display_name, icon_url = message.author.avatar_url_as(size=256))
		embed.set_footer(text=footer_text)

		await message.channel.send(file = preview_file, embed=embed)
		# os.system('rm saved/*')

	elif len(message.attachments) > 1:
		await message.channel.send("There were too many attachments.")
		return
	elif len(message.attachments) == 1 and message.content[4:] != '':
		await message.channel.send("Use either the content field or an attachment, not both.")
	elif len(message.attachments) == 1 and message.content[:3].lower() == 'pdf':
		# if the attachment is a markdown file, then use pandoc to convert it to a PDF and upload it.
		# if the attachment is a txt file, then save it as a markdown file anyway and do the same.
		# if it is any other type of file, send an error message.
		fn = message.attachments[0].filename
		ext = fn[fn.rfind('.'):]
		if ext not in ['.md', '.txt']:
			await message.channel.send("Wrong filetype.")
			return
		fn_md = fn if ext == '.md' else fn[:-len(ext)] + '.md'
		result = await message.attachments[0].save('saved/' + fn_md)
		print("Result from saving " + fn + ": " + str(result))

		filepath = fn_md

		pdf_path = pandoc(filepath[:-3])
		## use femto.pw for hosting
		femto_json = json.loads(subprocess.check_output('curl -F "upload=@' + pdf_path + '" https://v2.femto.pw/upload', shell=True))
		femto_url = "https://v2.femto.pw/" + femto_json['data']['short']
		print("femto_url: ", femto_url)
		print('femto_json: ', femto_json)

		preview_path = preview(filepath[:-3])
		preview_file = discord.File(preview_path)

		# create an embed to send things in
		# the thumbnail will be the file link
		# the image will be the preview image
		embed_title = "PDF link"
		embed_desc = "PDF requested by " + message.author.mention
		footer_text = "Comments or concerns? Issues? Contact thief#0001 or go to https://bots.thief.fyi."

		result = os.path.getsize('saved/' + filepath)
		pdfsize = os.path.getsize(pdf_path)
		pdf_pages = str(subprocess.check_output('qpdf --show-npages ' + pdf_path, shell=True))
		pdf_pages = pdf_pages[2:-3]
		size_text = "Size in bytes of plaintext: " + str(result) + '\nSize in bytes of output: ' + str(pdfsize) + '\nNumber of pages: ' + pdf_pages

		embed = discord.Embed(title = embed_title, description = embed_desc,color=discord.Color.teal(), url = femto_url)
		embed.add_field(name="Document Stats", value = size_text)
		#embed.add_field(name="Bot Info", value="PDF files are hosted at [femto.pw](https://v2.femto.pw)")
		embed.add_field(name="Preview Image", value = 'Below is a low-res preview of your PDF.', inline = False)
		embed.set_image(url="attachment://" + filepath[:-3] + ".png")
		embed.set_thumbnail(url = message.author.avatar_url_as(size=512))
		# embed.set_author(name = message.author.display_name, icon_url = message.author.avatar_url_as(size=256))
		embed.set_footer(text=footer_text)

		await message.channel.send(file = preview_file, embed=embed)
		# os.system('rm saved/*')
	else:
		filename = message.attachments[0].filename
		if filename[-4:] != '.png':
			await message.channel.send("Wrong filetype.")
			return
		await message.attachments[0].save('saved/' + filename)
		curl_out = subprocess.check_output("curl -F'file=@saved/" + filename + "' https://0x0.st", shell=True)
		await message.channel.send(message.author.mention + ": Your image, `" + filename[:-4] + "`, is hosted at " +
								   str(curl_out)[2:-3] + ". Markdown insert: `![" + filename[:-4] + "](" + str(curl_out)[2:-3] + ")`")
		return

def pandoc(filename): # creates a pdf from md
	os.system('pandoc -f markdown-implicit_figures saved/' + filename + '.md --pdf-engine=xelatex -o saved/' + filename + '.pdf')
	return 'saved/' + filename + '.pdf'

def preview(filename): # creates a png from pdf
	os.system('convert -background white -alpha remove -alpha off -quiet -density 125 -crop 750x500+105+105 saved/' + filename + '.pdf[0] -quality 50 saved/' + filename + '.png')
	# os.system('convert saved/' + filename + '.png -fill white -pointsize 50 -undercolor "#00000080" -gravity North +repage -annotate +0+0 "  PREVIEW " saved/' + filename + '_preview.png')
	# os.system('rm saved/' + filename + '.png')
	return 'saved/' + filename + '.png'# + '_preview.png'

bot.run(TOKEN)
