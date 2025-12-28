# Portrait Canvas Resizer

A web-based application for resizing and centering images on a white canvas with customizable padding. Designed for creating consistent image presentations across social media, portfolios, and digital content.

## Features

- White canvas framing with centered image placement
- Customizable canvas dimensions and padding
- Batch processing of multiple images
- Support for multiple image formats including HEIC
- Automatic EXIF orientation handling
- ZIP archive download of processed images
- Intuitive drag-and-drop web interface

## Prerequisites

- Docker
- Docker Compose

## Installation

Clone the repository:
```bash
git clone https://github.com/yourusername/portrait-canvas-resizer.git
cd portrait-canvas-resizer
```

Build and start the application:
```bash
docker-compose up --build
```

Access the application at `http://localhost:5000`

## Usage

### Configuration

Adjust the following settings in the web interface (default values provided):

- **Canvas Width**: 1080px
- **Canvas Height**: 1350px
- **Vertical Padding**: 32px
- **Horizontal Padding**: 114px

### Processing Images

1. Configure canvas and padding settings as needed
2. Upload images via drag-and-drop or file browser
3. Click "Process Images" to begin batch processing
4. Download the generated ZIP file containing all processed images

## Technical Details

### Image Processing Pipeline

The application performs the following operations on each image:

1. Loads the image and applies EXIF orientation corrections
2. Calculates optimal dimensions to fit within canvas bounds while maintaining aspect ratio
3. Applies specified padding (vertical or horizontal, whichever prevents canvas overflow)
4. Centers the resized image on a white canvas
5. Exports as JPEG with 95% quality

### Supported Formats

- JPEG/JPG
- PNG
- HEIC/HEIF
- BMP
- GIF
- TIFF

## Docker Management

Start the application:
```bash
docker-compose up
```

Start in detached mode:
```bash
docker-compose up -d
```

Stop the application:
```bash
docker-compose down
```

Rebuild after code changes:
```bash
docker-compose up --build
```

## Development

### Local Development Setup

Install Python 3.11 or higher, then install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Project Structure

```
portrait-canvas-resizer/
├── README.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── app.py
└── .gitignore
```

## Dependencies

- Python 3.11+
- Flask 3.0.0
- Pillow 10.1.0
- pillow-heif 0.14.0

## Default Configuration

| Parameter | Default Value |
|-----------|--------------|
| Canvas Width | 1080px |
| Canvas Height | 1350px |
| Vertical Padding | 32px |
| Horizontal Padding | 114px |
| Output Format | JPEG (95% quality) |

Default settings are optimized for Instagram portrait format (1080x1350) but can be customized for any use case.

## Use Cases

- Social media content standardization
- Portfolio and gallery presentations
- Product photography formatting
- Digital exhibition preparation
- E-commerce image consistency
- Brand asset management

## Technical Notes

- All images are converted to JPEG format upon export
- EXIF metadata is preserved for orientation but not included in output
- Image processing occurs entirely in-memory
- No user data or images are stored on the server
- Maximum upload size is limited by Flask defaults (16MB per file)

## Contributing

Contributions are welcome. Please submit pull requests with clear descriptions of changes and additions.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Security Considerations

- The application processes images in-memory and does not persist uploaded files
- All temporary data is cleared after processing
- Consider implementing rate limiting for production deployments
- File upload size limits should be configured based on deployment environment