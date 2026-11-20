import argparse
import sys
from pathlib import Path
from PIL import Image


def _pixel_data(image):
    # Pillow 14 removes getdata(); retain compatibility with Pillow 11.
    return getattr(image, 'get_flattened_data', image.getdata)()


def encode_text_to_image(input_path, output_path, message, terminator='\x00'):
    """
    Кодирует текст в изображение с использованием LSB-стеганографии.
    
    Args:
        input_path: Путь к исходному изображению
        output_path: Путь для сохранения результата
        message: Текст для кодирования
        terminator: Символ-терминатор для обозначения конца сообщения
    """
    if Path(output_path).suffix.lower() != '.png':
        raise ValueError("Сохраняйте результат в PNG: сжатие других форматов может повредить сообщение.")
    if not terminator or terminator in message:
        raise ValueError("Терминатор должен быть непустым и не встречаться в сообщении.")
    with Image.open(input_path) as img:
        # Конвертируем изображение в RGB/RGBA если необходимо
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')

        pixels = list(_pixel_data(img))
        # Преобразуем сообщение в бинарный формат
        message_bytes = (message + terminator).encode('utf-8')
        binary_str = ''.join(f"{byte:08b}" for byte in message_bytes)

        required_bits = len(binary_str)
        # Доступное количество бит (3 канала на пиксель)
        available_bits = len(pixels) * 3

        if required_bits > available_bits:
            raise ValueError(
                "Сообщение слишком длинное для изображения. "
                f"Требуется: {required_bits} бит, доступно: {available_bits} бит."
            )

        new_pixels = []
        bit_index = 0

        for pixel in pixels:
            new_channels = []
            # Обрабатываем каждый цветовой канал (R, G, B)
            for channel in pixel[:3]:
                if bit_index < required_bits:
                    # Заменяем младший бит
                    new_channel = (channel & 0xFE) | int(binary_str[bit_index])
                    bit_index += 1
                else:
                    new_channel = channel
                new_channels.append(new_channel)
            
            # Сохраняем альфа-канал если он есть
            new_pixels.append(tuple(new_channels + list(pixel[3:])))

        # Создаем новое изображение с закодированным сообщением
        new_img = Image.new(img.mode, img.size)
        new_img.putdata(new_pixels)
        new_img.save(output_path, format='PNG')
        return {
            'size': img.size,
            'message_bytes': len(message.encode('utf-8')),
            'required_bits': required_bits,
            'available_bits': available_bits,
        }


def decode_text_from_image(image_path, terminator='\x00'):
    """
    Декодирует текст из изображения.
    
    Args:
        image_path: Путь к изображению с закодированным сообщением
        terminator: Символ-терминатор для обозначения конца сообщения
    
    Returns:
        Декодированное сообщение
    """
    if not terminator:
        raise ValueError("Терминатор не может быть пустым.")
    terminator_bytes = terminator.encode('utf-8')
    with Image.open(image_path) as img:
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
        message_bytes = bytearray()
        byte = 0
        bit_count = 0
        for pixel in _pixel_data(img):
            for channel in pixel[:3]:
                byte = (byte << 1) | (channel & 1)
                bit_count += 1
                if bit_count != 8:
                    continue
                message_bytes.append(byte)
                byte = bit_count = 0
                if message_bytes.endswith(terminator_bytes):
                    try:
                        return message_bytes[:-len(terminator_bytes)].decode('utf-8')
                    except UnicodeDecodeError as exc:
                        raise ValueError("Скрытый текст повреждён или не является UTF-8.") from exc
    raise ValueError("Конец сообщения не найден: изображение не содержит сообщения или повреждено.")


def print_panel(title, lines):
    """Компактный вывод; ANSI-цвета включаются только в терминале."""
    color = sys.stdout.isatty()
    accent = '\033[96m' if color else ''
    reset = '\033[0m' if color else ''
    print(f"\n{accent}+--- IMAGESTEG / {title} ---+{reset}")
    for line in lines:
        print(f"  {line}")
    print(f"{accent}+{'-' * 44}+{reset}")


def main():
    """Основная функция для обработки аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description='Инструмент стеганографии для кодирования/декодирования сообщений в изображениях.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Примеры использования:\n'
               '  Кодирование: python imagesteg.py --input input.png --output output.png --message "Секретное сообщение"\n'
               '  Декодирование: python imagesteg.py --decode --input output.png'
    )
    parser.add_argument('--decode', action='store_true', 
                        help='Режим декодирования')
    parser.add_argument('--input', type=str, required=True,
                        help='Путь к исходному изображению')
    parser.add_argument('--output', type=str,
                        help='Путь для сохранения результата (режим кодирования)')
    parser.add_argument('--message', type=str,
                        help='Сообщение для кодирования')

    args = parser.parse_args()

    if not args.decode and (not args.output or args.message is None):
        parser.error("Для кодирования необходимы аргументы --output и --message")

    try:
        if args.decode:
            decoded_message = decode_text_from_image(args.input)
            print_panel("СЕКРЕТ РАСКРЫТ", ["Сообщение:", decoded_message])
        else:
            stats = encode_text_to_image(args.input, args.output, args.message)
            ratio = stats['required_bits'] / stats['available_bits']
            filled = round(ratio * 24)
            bar = '#' * filled + '.' * (24 - filled)
            width, height = stats['size']
            print_panel("МИССИЯ ВЫПОЛНЕНА", [
                f"Контейнер: {width} x {height} px",
                f"Спрятано: {stats['message_bytes']} байт текста",
                f"Заполнение: [{bar}] {ratio:.1%}",
                f"Файл: {args.output}",
                "Пиксели хранят ваш секрет.",
            ])
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
