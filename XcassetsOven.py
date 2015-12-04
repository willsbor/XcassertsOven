import getopt
import ntpath
import sys
import os
import io
import json
import shutil
from PIL import Image
from collections import OrderedDict

class XcassetsOvenErrorException(Exception):
    pass

class XcassetsOvenNotSupportTypeException(Exception):
    pass

def find_image_file(a_dir, a_extension_name='.png'):
    result = []
    for name in os.listdir(a_dir):
        full_path = os.path.join(a_dir, name)
        #print name
        #print full_path
        if os.path.isdir(full_path):
            result.extend(find_image_file(full_path,a_extension_name))
        elif name.endswith(a_extension_name):
            #print 'find ' + name
            result.append(full_path)
    return result

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def path_head(path):
    head, tail = ntpath.split(path)
    return ntpath.basename(head)

def filename_without_ext_type(a_filename):
    filenames = a_filename.split('.')
    return ".".join(filenames[:-1])

def filename_without_scale_number(a_filename):
    filenames = a_filename.split('@')
    if len(filenames) == 1:
        return a_filename
    else:
        return "@".join(filenames[:-1])

def init_content(a_type):
    author = 'xcode'
    if a_type == 'imageset':
        return {
            'images': [],
            'info': {
                'version': 1,
                'author': author,
            },
        }
    elif a_type == 'appiconset':
        return {
            'images': [],
            'info': {
                'version': 1,
                'author': author,
            },
            'properties' : {
                'pre-rendered' : True
            }
        }
    elif a_type == 'launchimage':
        return {
            'images': [],
            'info': {
                'version': 1,
                'author': author,
            },
        }
    elif a_type == 'xcassets':
        return {
            'info': {
                'version': 1,
                'author': author,
            },
        }
    else:
        raise XcassetsOvenNotSupportTypeException({"message": "Not support this type", "type": a_type})

def _info_by_size(filename, idiom, size, scale):
    return {'filename': filename, 'idiom': idiom, 'size': "" + str(size / scale) + "x" + str(size / scale), 'scale': "" + str(scale) + "x"}

def init_infos_content(a_type, a_filename, a_path):
    infos = []
    
    if a_type == 'imageset':
        sort_order = ['idiom', 'scale', 'filename', 'A10']
        items = {'filename': a_filename, 'idiom': 'universal', 'scale': guess_scale_by_filename(a_filename)}
        items_ordered = [OrderedDict(sorted(item.iteritems(), key=lambda (k, v): sort_order.index(k)))
                    for item in items]
        infos.append(items_ordered)
    elif a_type == 'appiconset':
        im = Image.open(a_path)
        xsize, ysize = im.size
        if xsize != ysize:
            raise XcassetsOvenErrorException({"message": "size incorrect", "size": im.size})

        if xsize == 29:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 1))
        elif xsize == 58:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 2))
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 2))
        elif xsize == 87:
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 3))
        elif xsize == 40:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 1))
        elif xsize == 80:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 2))
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 2))
        elif xsize == 120:
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 3))
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 2))
        elif xsize == 180:
            infos.append(_info_by_size(a_filename, 'iphone', xsize, 3))
        elif xsize == 76:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 1))
        elif xsize == 152:
            infos.append(_info_by_size(a_filename, 'ipad', xsize, 2))
        else:
            raise XcassetsOvenErrorException({"message": "size unsupport", "size": im.size})
    elif a_type == 'launchimage':
        im = Image.open(a_path)
        xsize, ysize = im.size

        if xsize == 1242 and ysize == 2208:
            infos.append({'filename': a_filename, 'extent': 'full-screen', 'idiom': 'iphone', 'subtype': '736h', 'scale': '3x', 'orientation': 'portrait', 'minimum-system-version' : '8.0'})
        elif xsize == 750 and ysize == 1334:
            infos.append({'filename': a_filename, 'extent': 'full-screen', 'idiom': 'iphone', 'subtype': '667h', 'scale': '2x', 'orientation': 'portrait', 'minimum-system-version' : '8.0'})
        elif xsize == 640 and ysize == 1136:
            infos.append({'filename': a_filename, 'extent': 'full-screen', 'idiom': 'iphone', 'subtype': 'retina4', 'scale': '2x', 'orientation': 'portrait', 'minimum-system-version' : '7.0'})
        elif xsize == 640 and ysize == 960:
            infos.append({'filename': a_filename, 'extent': 'full-screen', 'idiom': 'iphone', 'scale': '2x', 'orientation': 'portrait', 'minimum-system-version' : '7.0'})
        else:
            raise XcassetsOvenErrorException({"message": "size unsupport", "size": im.size})
    else:
        raise XcassetsOvenNotSupportTypeException({"message": "Not support this type", "type": a_type})
    return infos

def guess_scale_by_filename(a_filename, a_filepath = ''):
    if a_filename.find('@2x') != -1:
        return '2x'
    elif a_filename.find('@3x') != -1:
        return '3x'
    else:
        return '1x'

def modify_info(a_info, a_given_info):
    a_info["scale"] = a_given_info["scale"]

def append_infos_into_content(a_sub_images, a_main_images, a_type):
    # add into [] by 
    # - imageset: scale + idiom or 
    # - appiconset:  size + scale + idiom 
    # - launchimage: subtype scale orientation

    for info in a_sub_images:
        ishit = False
        for m_info in a_main_images:
            if 'launchimage' == a_type:
                if info['scale'] == m_info['scale'] and info['orientation'] == m_info['orientation']:
                    if 'subtype' in info and info['subtype'] == m_info['subtype']:
                        ishit = True
            elif info['idiom'] == m_info['idiom'] and info['scale'] == m_info['scale']:
                if 'size' in info:
                    if info['size'] == m_info['size']:
                        ishit = True
                else:
                    ishit = True

        if ishit:
            raise XcassetsOvenErrorException({"message": "duplicate setting for contents.json", "info": json.dumps(info), "main_images": json.dumps( a_main_images)})
        else:
            a_main_images.append(dict(info))

def create_xcassets_by_images(a_input_dir, a_result_dir, a_info_map, a_contents_map):
    if os.path.exists(a_result_dir):
        shutil.rmtree(a_result_dir)

    all_image_files = find_image_file(a_input_dir)

    # create sub xcassets dir
    for path in all_image_files:
        # get parent dir
        relative_path = path.replace(a_input_dir + "/", "")
        category_path = path_head(path)
        filename = path_leaf(path)

        if filename in a_info_map:
            if a_info_map[filename]['state'] == 'once':
                raise XcassetsOvenErrorException({"message": "filename is duplicated", "filename": filename, "category_path": category_path})

            print "get from infos.txt [" + relative_path + "]"
            a_info_map[filename]['state'] = 'once'
            set_name = a_info_map[filename]["set"]
            set_type = a_info_map[filename]["type"]
        else:
            print "parse by filename [" + relative_path + "]"
            set_name = filename_without_ext_type(filename)
            set_name = filename_without_scale_number(set_name)
            set_type = "imageset"
            a_info_map[filename] = {}
            a_info_map[filename]['state'] = 'once'
            a_info_map[filename]['type'] = set_type
            a_info_map[filename]['set'] = set_name
            a_info_map[filename]['images'] = None

        set_content_file = a_result_dir + "/" + category_path + ".xcassets" + "/" + "Contents.json"
        if set_content_file not in a_contents_map:
           a_contents_map[set_content_file] = init_content('xcassets')

        content_file = a_result_dir + "/" + category_path + ".xcassets" + "/" + set_name + "." + set_type + "/Contents.json"
        if content_file not in a_contents_map:
            a_contents_map[content_file] = init_content(set_type)
        content = a_contents_map[content_file]


        if filename in a_info_map and a_info_map[filename]['images']:
            append_infos_into_content(a_info_map[filename]['images'], content['images'], set_type)
        else:
            infos = init_infos_content(set_type, filename, path)
            for info in infos:
                if a_info_map[filename]['images'] is None:
                    a_info_map[filename]['images'] = []
                a_info_map[filename]['images'].append(info)
                content['images'].append(info)

        # TODO: add more type or resize image if it lose

        dst = a_result_dir + "/" + category_path + ".xcassets" + "/" + set_name + "." + set_type + "/" + filename
        directory = os.path.dirname(dst)
        if not os.path.exists(directory):
            os.makedirs(directory)
        shutil.copyfile(path, dst)

def get_contents_map(a_input_dir):
    all_content_files = find_image_file(a_input_dir, '.json')

    content_map = {}
    # create sub xcassets dir
    for path in all_content_files:
        relative_path = path.replace(a_input_dir + "/", "")

        head, filename = ntpath.split(relative_path)
        category, set_name_type = ntpath.split(head)
        set_name, set_type = set_name_type.split('.', 2)
        category = category.split('.')[0]

        info = json_dict_for_file_path(path)
        content_map[set_name] = info

    return content_map

def get_specific_filename(a_content_map, a_filename):
    result = []
    for info in a_content_map['images']:
        if 'filename' in info and info['filename'] == a_filename:
            result.append(info)
    return result

def parse_xcassets(a_input_dir, a_result_dir, info_file):
    if a_result_dir is not None and os.path.exists(a_result_dir):
        shutil.rmtree(a_result_dir)

    content_map = get_contents_map(a_input_dir)
    all_image_files = find_image_file(a_input_dir)

    info_map = {}
    # create sub xcassets dir
    for path in all_image_files:
        # get parent dir
        relative_path = path.replace(a_input_dir + "/", "")

        head, filename = ntpath.split(relative_path)
        category, set_name_type = ntpath.split(head)
        set_name, set_type = set_name_type.split('.', 2)
        category = category.split('.')[0]

        if filename in info_map:
            raise XcassetsOvenErrorException({"message": "duplicate filename", "filename": filename, "relative_path": relative_path})

        info = {}
        info['state'] = 'ok'
        info['set'] = set_name
        info['type'] = set_type
        info['images'] = get_specific_filename(content_map[set_name], filename)
        info_map[filename] = info

        if a_result_dir is not None:
            dst = a_result_dir + "/" + category + "/" + filename
            directory = os.path.dirname(dst)
            if not os.path.exists(directory):
                os.makedirs(directory)
            shutil.copyfile(path, dst)

    write_info_map(info_file, info_map)

def read_info_map(a_filepath):
    if not os.path.exists(a_filepath):
        return {}

    infos_map = {}
    with open(a_filepath) as f:
        content = f.readlines()
        for line in content:
            line = line[:-1]  # remove \n
            infos = line.split(", ", 4)
            if len(infos) == 5:
                infos_map[infos[1]] = {}
                infos_map[infos[1]]["state"] = infos[0]
                infos_map[infos[1]]["set"] = infos[2]
                infos_map[infos[1]]["type"] = infos[3]
                infos_map[infos[1]]["images"] = json.loads(infos[4])
            else:
                print "false : [" + str(len(infos)) + "]" + line
    return infos_map

def write_info_map(a_filepath, a_info_map):
    directory = os.path.dirname(a_filepath)
    if directory != '' and not os.path.exists(directory):
        os.makedirs(directory)

    f = io.open(a_filepath, 'wb')
    for info_key in iter(a_info_map):
        info = a_info_map[info_key]
        f.write("" + "ok" + ", " + info_key + ", " + info['set'] + ", " + info['type'] + ", " + json.dumps(info['images'], sort_keys=True) + "\n")
    f.close()

def json_dict_for_file_path(file_path):
    if os.path.exists(file_path):
        return json.load(open(file_path, 'r'))
    return None

def write_dict_to_file_path(file_path, info):
    json_file = open(file_path, 'w+')
    json_file.write(json.dumps(info, indent=2, separators=(',',' : ')))
    json_file.close()

def create_contents_files(a_contents_map):
    for path in iter(a_contents_map):
        content = a_contents_map[path]
        write_dict_to_file_path(path, content)

def main(argv):

    images_dir = None
    result_dir = None
    info_file = "xcassets_info.txt"
    command = None

    try:
        opts, args = getopt.getopt(argv,
            "ho:c:p:i:",
            ["output=","create-xcassets=","parse-xcassets=","info-file="])
    except getopt.GetoptError:
        print 'error: parse.py wrong command'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
           print 'parse.py ????'
           sys.exit()
        elif opt in ("-c", "--create-xcassets"):
            command = "c"
            images_dir = arg
        elif opt in ("-p", "--parse-xcassets"):
            command = "p"
            images_dir = arg
        elif opt in ("-o", "--output"):
            result_dir = arg
        elif opt in ("-i", "--info-file"):
            info_file = arg

    if images_dir is not None:
        images_dir = os.path.abspath(os.path.normpath(images_dir))
    if result_dir is not None:
        result_dir = os.path.abspath(os.path.normpath(result_dir))
    if info_file is not None:
        info_file = os.path.abspath(os.path.normpath(info_file))

    print "source_dir = " + str(images_dir)
    print "output = " + str(result_dir)
    print "info file = " + str(info_file)

    if command == "c":
        info_map = read_info_map(info_file)
        contents_map = {}
        create_xcassets_by_images(images_dir, result_dir, info_map, contents_map)
        create_contents_files(contents_map)
        write_info_map(info_file, info_map)
    elif command == "p":
        parse_xcassets(images_dir, result_dir, info_file)
    else:
        print 'parse.py ????'
        sys.exit()
   
if __name__ == "__main__":
   main(sys.argv[1:])