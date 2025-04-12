# PolicyDecoderAI

A powerful AI-enhanced civic education app that helps people understand government policies through ensemble learning and advanced language models.

## Features

- 🤖 Ensemble AI Analysis using multiple models (OpenAI GPT and Anthropic Claude)
- 📚 High School Level Explanations
- 📊 Multiple Analysis Modes
- 📝 Document Upload and Processing
- 🔄 Interactive Follow-up Questions
- 📋 Session History Tracking

## Setup

1. Clone the repository:
```bash
git clone https://github.com/mt-davis/pdecdoer.git
cd pdecdoer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

4. Run the application:
```bash
streamlit run app.py
```

## Project Structure

- `/chains` - LangChain implementations
- `/components` - Reusable UI components
- `/pages` - Streamlit pages
- `/utils` - Utility functions
- `app.py` - Main application entry point

## Usage

1. Upload a policy document (PDF) or paste policy text
2. Select analysis mode
3. Toggle high school level explanations if needed
4. Ask questions about the policy
5. View ensemble analysis from multiple AI models

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request