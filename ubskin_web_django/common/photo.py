import os
import subprocess
import uuid

from PIL import Image

# photo_specs = {
#     "title": {"width": 300, "height": 200},
#     "thumbicon": {"width": 180, "is_square": True},
#     "item_title": { "width": 300, "is_square": True},
#     "item": {"width": 980},
#     "brand": {"width": 300, "is_square": True},
#     "comment": {"width": 300, "height": 400}
# }

photo_specs = [
    {"type": "thumb", "width": 180, "is_square": True},
    {"type": "thumbicon", "width": 100, "is_square": True},
    {"type": "title", "width": 300, "is_square": True},
    {"type": "item", "width": 650},
]

# pic_specs = [
#     {"type": "mpic", "pixel": 14500, "quality": 88},
#     {"type": "spic", "pixel": 6500, "quality": 88}
# ]

def convert_photo(photo_id, base_static_path, photo_type="photo", 
        is_from_source=False):
    if is_from_source:
        f_path_raw = os.path.join(base_static_path, "source", "photos", "raw",
            photo_id[:2], photo_id+".jpg"
        )
    else:
        f_path_raw = os.path.join(base_static_path, 'photos', "raw", photo_id[0:2], photo_id + ".jpg")
    image_obj = Image.open(f_path_raw)
    image_obj = image_obj.convert('RGB')
    target_specs = photo_specs
    target_path_name = "photos"
    # if photo_type == "pic":
    #     target_specs = pic_specs
    #     target_path_name = "pics"
    new_image_obj = None
    width = None
    height = None
    for spec in target_specs:
        d_path_target = os.path.join(
            base_static_path,
            target_path_name,
            spec['type'],
            photo_id[:2]
        )
        if not os.path.exists(d_path_target):
            os.makedirs(d_path_target)
        if spec.get("is_square") and spec["is_square"]:
            width, height = image_obj.size
            if width > height:
                left_cent_size =  int((width - height)/2)
                right_cent_size = width - left_cent_size
                new_image_obj = image_obj.crop((left_cent_size, 0, right_cent_size, height))
            elif height > width:
                top_cent_size = int((height - width)/2)
                bottom_cent_size = height - top_cent_size
                new_image_obj = image_obj.crop((0, top_cent_size, width, bottom_cent_size))
            else:
                new_image_obj = image_obj.crop((0, 0, width, width))
            width = spec['width']
            new_image_obj = new_image_obj.resize((width, width), Image.ANTIALIAS)
            width, height = spec['width'], spec['width']
        elif spec.get("width") and spec.get("height"):
            if spec.get('is_crop') and spec['is_crop']:
                width, height = image_obj.size
                left_cent_size = int((width - spec['width'])/2)
                right_cent_size = width - left_cent_size
                top_cent_size = int((height - spec['height'])/2)
                bottom_cent_size = height - top_cent_size
                new_image_obj = image_obj.crop((
                    left_cent_size,
                    top_cent_size,
                    right_cent_size,
                    bottom_cent_size
                ))
                width, height = spec['width'], spec['height']
            else:
                width = spec["width"]
                height = spec["height"]
                new_image_obj = image_obj.resize(
                    (width, height),
                    Image.ANTIALIAS
                )
        elif spec.get('width') and not spec.get('height'):
            width, height = image_obj.size
            spec_width = spec['width']
            if width > spec_width:
                scaling_percentage = spec_width/width
                height = int(scaling_percentage * height)
                new_image_obj = image_obj.resize((spec_width, height), Image.ANTIALIAS)
                width, height = spec_width, height
            else:
                new_image_obj = image_obj.resize((width, height), Image.ANTIALIAS)
        convert_photo_path = os.path.join(d_path_target, photo_id + ".jpg")
        new_image_obj.save(convert_photo_path)
    return {
        "file_size":os.path.getsize(convert_photo_path),
        "resolution":"{0}*{1}".format(width, height),
        'file_type':'jpg'
    }

def save_upload_photo(photo_file, base_static_path):
    photo_id = uuid.uuid4().hex
    d_path_raw = os.path.join(base_static_path, 'photos', "raw", photo_id[0:2])
    f_path_raw = os.path.join(d_path_raw, photo_id + ".jpg")
    if not os.path.exists(d_path_raw):
        os.makedirs(d_path_raw)
    with open(f_path_raw, "wb") as f:
        for chunk in photo_file.chunks():
            f.write(chunk)
    data = convert_photo(photo_id, base_static_path)
    data.update({"photo_id" : photo_id})
    return data
   


# def remove_photo(photo_id, base_static_path, photo_type="photo"):
#     target_specs = photo_specs
#     target_path_name = "photos"
#     if photo_type == "pic":
#         target_specs = pic_specs
#         target_path_name = "pics"

#     for spec in target_specs:
#         f_path_target = os.path.join(base_static_path, target_path_name, spec["type"],
#             photo_id[:2], photo_id + ".jpg"
#         )
#         try:
#             os.remove(f_path_target)
#         except OSError:
#             pass


# def get_photo_size(photo_id):
#     f_path_raw = os.path.join(base_static_path, "photos", "raw", photo_id[:2],
#                               photo_id + ".jpg"
#     )

#     cmd_identify = "gm identify -format \"%m|%w|%h\" " + f_path_raw
#     popen = subprocess.Popen(cmd_identify, shell=True, stdout=subprocess.PIPE)
#     cmd_code = popen.wait()
#     cmd_output = popen.stdout.read()
#     output_list = cmd_output.split("|")

#     if cmd_code == 0 and len(output_list) == 3:
#         return (output_list[1], output_list[2])
#     else:
#         return None