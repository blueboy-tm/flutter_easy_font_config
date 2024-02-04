from fontTools.ttLib import TTFont
import os
import shutil
import argparse

weight_mapping = {
    100: 'Thin',
    200: 'ExtraLight',
    300: 'Light',
    400: 'Regular',
    500: 'Medium',
    600: 'SemiBold',
    700: 'Bold',
    800: 'ExtraBold',
    900: 'Black',
}


def mkdir(path):
    if not os.path.exists(path):
        os.mkdir(path)


def round_down_to_increment(number, increment=100):
    return (number // increment) * increment


fonts = {}


def get_font_name(family, weight, italic):
    if weight == 400:
        suffix = 'Italic' if italic else 'Regular'
    else:
        suffix = weight_mapping.get(weight, 'Unknow')
        if italic:
            suffix += 'Italic'

    return f'{family}-{suffix}.ttf'


def add_font(font_path):
    try:
        font = TTFont(font_path)
        fontWeight = round_down_to_increment(font['OS/2'].usWeightClass)
        fontFamily = font['name'].getDebugName(4).split(' ')[0]
        italic = bool(font['post'].italicAngle)
        path = os.path.join(fontFamily, get_font_name(
            fontFamily, fontWeight, italic))
        f = fonts.get(fontFamily, [])
        f.append({'weight': fontWeight, 'italic': italic, 'path': path})
        fonts[fontFamily] = f
        mkdir(os.path.join(output_path, fontFamily))
        shutil.copy(font_path, os.path.join(output_path, path))
    except Exception as e:
        return


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='flutter_easy_font_config',
        description='Creating automatic configuration for pubspec.yaml and sorting font names')
    parser.add_argument('path', help='The path where fonts are located')
    parser.add_argument('-o', '--output', required=False,
                        default='output', help='Output path of edited fonts')
    parser.add_argument('-p', '--prefix', required=False,
                        default='', help='The path where you put the fonts in the Fluttery project, for example assets')
    args = parser.parse_args()
    fonts_path = args.path
    output_path = args.output
    asset_prefix = args.prefix
    for i in os.listdir(fonts_path):
        add_font(os.path.join(fonts_path, i))

    fonts = {key: sorted(value, key=lambda x: x["weight"])
             for key, value in fonts.items()}
    print('  fonts:')
    for i in sorted(fonts):
        family = fonts[i]
        print(f'    - family: {i}')
        print(f'      fonts:')
        for font in family:
            print(
                '        - asset: {}'.format(os.path.join(asset_prefix, font.get('path'))))
            if font.get('weight') != 400:
                print('          weight: {}'.format(font.get('weight')))
            if font.get('italic'):
                print('          style: italic')
        print('')
