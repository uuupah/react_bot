import requests
import io
import discord
import glob
from PIL import Image as image
from util.now import now

# this is imported multiple times and should be done properly
shitmoop = 811211114699292672
learn2spell = 'https://www.youtube.com/watch?v=jfzsa0DDc0o'

# load in images
# overlay = image.open('assets/a.png')
# overlay_l = image.open('assets/left.png')
# overlay_r = image.open('assets/right.png')
def get_overlays():
    out = {}
    for filename in glob.glob('assets/overlays/*.png'):
        out[filename
            .replace('assets/overlays/', '')
            .replace('.png', '')] = image.open(filename)
    return out

# TODO add orientation argument to push to left or right or top or bottom
async def soy(msg, style=None):
    im = get_overlays()

    print(f'$$ Bot pinged, searching for images {now()}')
    async for message in msg.channel.history(limit=20):
        if message.attachments:
            atch = message.attachments[len(message.attachments)-1]
            # TODO iterate through files if the end isnt an image
            if atch.content_type.startswith("image/"):
                print(
                    f'$$ Image found at {atch.url} {now()}')

                backgr = image.open(requests.get(atch.url, stream=True).raw)

                if style == None:
                    style = 'soy'
                elif style not in im:
                    await msg.channel.send(learn2spell)
                    return

                # get aspect ratios
                backgr_ar = backgr.size[0] / backgr.size[1]
                overlay_ar = im['soy'].size[0] / im['soy'].size[1]

                print(f'$$ Generating new image with overlay {now()}')

                # todo reorg
                # if backgr image is wider than original overlay, and an _l and
                # _r version of the current overlay exist, split the
                # image and paste the halves separately
                if backgr_ar > overlay_ar and im[style + '_l'] in im and im[style + '_r'] in im:
                    backgr = _wide_overlay_split(
                        backgr, style + '_l', style + '_r')
                elif backgr_ar > overlay_ar:
                    backgr = _wide_overlay_centre(backgr, im[style])
                #   place the single image on the background
                # else just do it the easy way
                else:
                    backgr = _narrow_overlay(backgr, im[style])

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
    # overlay_l = im[style_l]
    # overlay_r = im[style_r]
    backgr_h = backgr.size[1]  # background height
    # get ratio of current height to background height
    l_h_ratio = (backgr_h / float(overlay_l.size[1]))
    # get target width using current width and ratio
    l_w_target = int((float(overlay_l.size[0]) * float(l_h_ratio)))
    t_overlay_l = overlay_l.resize(
        (l_w_target, backgr_h), image.ANTIALIAS)  # resize

    backgr.paste(
        t_overlay_l, (0, backgr.size[1] - t_overlay_l.size[1]), t_overlay_l)

    r_h_ratio = (backgr_h / float(overlay_r.size[1]))
    r_w_target = int((float(overlay_r.size[0]) * float(r_h_ratio)))
    t_overaly_r = overlay_r.resize((r_w_target, backgr_h), image.ANTIALIAS)

    backgr.paste(t_overaly_r, (backgr.size[0] - t_overaly_r.size[0],
                 backgr.size[1] - t_overaly_r.size[1]), t_overaly_r)
    return backgr


def _wide_overlay_centre(backgr, overlay):
    # overlay = im[style]
    # find height of background image
    backgr_h = backgr.size[1]
    # resize overlay to ratio according to background image height
    h_ratio = (backgr_h / float(overlay.size[1]))
    w_target = int(float(overlay.size[0]) * float(h_ratio))
    print(f'background height: {backgr_h}')
    print(f'background width: {w_target}')
    t_overlay = overlay.resize((w_target, backgr_h), image.ANTIALIAS)
    # if overlay name ends in _l
    #   overlay image on background on the left
    # if overlay name ends in _r
    #   overlay image on background on the right
    # else
    #   overlay image on background in the centre
    backgr.paste(t_overlay, (int(
        (0.5 * float(backgr.size[0]))-(0.5 * float(w_target))), 0), t_overlay)
    return backgr


def _narrow_overlay(backgr, overlay):
    # overlay = im[style]
    backgr_w = backgr.size[0]  # background width
    w_ratio = (backgr_w / float(overlay.size[0]))
    h_target = int(float(overlay.size[1]) * float(w_ratio))
    t_overlay = overlay.resize((backgr_w, h_target), image.ANTIALIAS)

    backgr.paste(t_overlay, (0, backgr.size[1] - t_overlay.size[1]), t_overlay)
    return backgr
