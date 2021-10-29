import requests
import io
import discord
import glob
from PIL import Image as image
from util.now import now

# this is imported multiple times and should be done properly
shitmoop = 811211114699292672

# load in images
overlay = image.open('assets/a.png')
overlay_l = image.open('assets/left.png')
overlay_r = image.open('assets/right.png')

im = {}

for filename in glob.glob('assets/overlays/*.png'):
    im[filename
        .replace('assets/overlays/','')
        .replace('.png','')] = image.open(filename)

print(im)

async def soy(msg):
    print(f'$$ Bot pinged, searching for images {now()}')
    async for message in msg.channel.history(limit=20):
        if message.attachments:
            # TODO iterate through files if the end isnt an image
            if message.attachments[len(message.attachments) -
                                   1].content_type.startswith("image/"):
                print(
                    f'$$ Image found at {message.attachments[len(message.attachments)-1].url} {now()}'
                )

                backgr = image.open(
                    requests.get(message.attachments[len(message.attachments) -
                                                     1].url,
                                 stream=True).raw)

                # get aspect ratios
                backgr_ar = backgr.size[0] / backgr.size[1]
                overlay_ar = overlay.size[0] / overlay.size[1]

                print(f'$$ Generating new image with overlay {now()}')

                # if backgr image is wider than original overlay, split the image and paste the halves separately
                if backgr_ar > overlay_ar:
                    backgr = _wide_overlay_split(backgr, overlay_l, overlay_r)
                # otherwise, just do it the easy way
                else:
                    backgr = _narrow_overlay(backgr, overlay)

                print(f'$$ New image generation complete {now()}')

                # post image
                with io.BytesIO() as image_binary:
                    backgr.save(image_binary, 'PNG', optimize=True, quality=90)
                    image_binary.seek(0)
                    await message.channel.send(file=discord.File(
                        fp=image_binary, filename='image.png'))

                print(f'$$ Reaction image posted {now()}')
                return

    print(f'$$ no images found {now()}')
    await msg.channel.send(f'<:moop:{shitmoop}>')
    return

def _wide_overlay_split(backgr, overlay_l, overlay_r):
    backgr_h = backgr.size[1]  # background height
    l_h_ratio = (
        backgr_h / float(overlay_l.size[1])
    )  # get ratio of current height to background height
    l_w_target = int(
        (float(overlay_l.size[0]) * float(l_h_ratio)
            ))  # get target width using current width and ratio
    t_overlay_l = overlay_l.resize((l_w_target, backgr_h),
                                    image.ANTIALIAS)  # resize

    backgr.paste(t_overlay_l,
                    (0, backgr.size[1] - t_overlay_l.size[1]),
                    t_overlay_l)

    r_h_ratio = (backgr_h / float(overlay_r.size[1]))
    r_w_target = int(
        (float(overlay_r.size[0]) * float(r_h_ratio)))
    t_overaly_r = overlay_r.resize((r_w_target, backgr_h),
                                    image.ANTIALIAS)

    backgr.paste(t_overaly_r,
                    (backgr.size[0] - t_overaly_r.size[0],
                    backgr.size[1] - t_overaly_r.size[1]),
                    t_overaly_r)
    return backgr

def _wide_overlay(backgr, overlay):
    return backgr

def _narrow_overlay(backgr, overlay):
    backgr_w = backgr.size[0]  # background width
    w_ratio = (backgr_w / float(overlay.size[0]))
    h_target = int((float(overlay.size[1]) * float(w_ratio)))
    t_overlay = overlay.resize((backgr_w, h_target),
                               image.ANTIALIAS)

    backgr.paste(t_overlay,
                 (0, backgr.size[1] - t_overlay.size[1]),
                 t_overlay)
    return backgr