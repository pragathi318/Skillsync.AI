# 🤖 AI Mock Interview Onboarding

A premium, glossy-style AI chatbot for mock interview onboarding. Built with **Next.js 15**, **Tailwind CSS**, and **OpenAI/OpenRouter** integration.

![Project Preview](/placeholder-image.png)

## ✨ Features

- **Apple-Style Glossy UI**: Premium glassmorphism design with refined animations and "shiny" aesthetics.
- **Interactive Chat**: Real-time AI conversation powered by GPT-4o-mini (via OpenRouter).
- **Resume Upload**: Seamless file upload functionality with automatic resume parsing.
- **Generative Background**: Dynamic 3D mountain landscape using Three.js.
- **Responsive Design**: Fully responsive layout that works on desktop and mobile.

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

- **Node.js**: Version 18.17 or later.
- **npm**: Comes with Node.js.

### Installation

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone <your-repo-url>
    cd AI-mock-interview-main
    ```

2.  **Install dependencies**:
    ```bash
    npm install
    # or
    npm install --legacy-peer-deps
    ```

3.  **Environment Setup**:
    Create a `.env` file in the root directory (or use the existing one) and add your API keys:

    ```env
    OPENROUTER_API_KEY=your_openrouter_api_key_here
    BLOB_READ_WRITE_TOKEN=your_vercel_blob_token_here
    ```

### 🏃 Running Locally

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## 🛠️ Build for Production

To create an optimized production build:

```bash
npm run build
```

To start the production server:

```bash
npm start
```

## ☁️ Deployment on Vercel

The easiest way to deploy this Next.js app is to use the [Vercel Platform](https://vercel.com/new).

1.  **Push to Git**: Ensure your code is pushed to a GitHub, GitLab, or Bitbucket repository.
2.  **Import Project**: Go to Vercel, click "Add New...", and import your repository.
3.  **Configure Environment Variables**: Add the `OPENROUTER_API_KEY` and `BLOB_READ_WRITE_TOKEN` in the Vercel project settings.
4.  **Deploy**: Click "Deploy". Vercel will automatically detect Next.js and build your site.

## 📂 Project Structure

- `src/app/page.js`: Main entry point and layout structure.
- `src/app/api/chat`: Backend API route handling AI logic.
- `src/components/ui/ai-chat.js`: Core Chat Interface component.
- `src/components/ui/mountain-scene.js`: 3D background animation.
- `src/app/globals.css`: Global styles including the glassmorphism effects.

## 🤝 Contributing

1.  Fork the project
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request
