import React, { useState } from 'react';

const SpiritualGuidance = () => {
  const [selectedGuru, setSelectedGuru] = useState('');
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const gurus = [
    { id: 'spiritual', name: '🙏 Spiritual Guru', description: 'Soul consciousness & eternal identity' },
    { id: 'sloka', name: '🕉️ Sloka Guru', description: 'Sanskrit verses & sacred wisdom' },
    { id: 'meditation', name: '🧘 Meditation Guru', description: 'Inner peace & emotional healing' },
    { id: 'bhakti', name: '💝 Bhakti Guru', description: 'Devotion & divine love' },
    { id: 'karma', name: '⚖️ Karma Guru', description: 'Ethics & dharma' },
    { id: 'yoga', name: '🧘‍♀️ Yoga Guru', description: 'Breath & energy alignment' },
  ];

  const askSpiritual = async () => {
    if (!selectedGuru || !question.trim()) {
      alert('Please select a guru and enter your question');
      return;
    }

    setIsLoading(true);
    setResponse('');

    try {
      const response = await fetch('/api/ask-guru', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          guru_type: selectedGuru,
          question: question.trim()
        })
      });

      const data = await response.json();

      if (data.success) {
        setResponse(data.response);
      } else {
        setResponse('🙏 The guru is in deep meditation. Please try again.');
      }
    } catch (error) {
      setResponse('🌸 Connection interrupted. Please ensure the API is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">
          🕉️ AI Empower Heart 360
        </h1>
        <p className="text-xl text-white/80">
          Awakening Your Inner Self Through Ancient Wisdom & AI Guidance
        </p>
      </div>

      <div className="bg-white/10 backdrop-blur-md rounded-3xl p-8">
        <h2 className="text-2xl font-bold text-white text-center mb-8">
          Choose Your Spiritual Guide
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {gurus.map((guru) => (
            <div
              key={guru.id}
              onClick={() => setSelectedGuru(guru.id)}
              className={`
                p-6 rounded-2xl cursor-pointer transition-all duration-300 
                ${selectedGuru === guru.id
                  ? 'bg-gradient-to-r from-yellow-400/30 to-yellow-300/30 border-2 border-yellow-400 transform scale-105'
                  : 'bg-white/20 border-2 border-transparent hover:bg-white/30 hover:scale-105'
                }
              `}
            >
              <h3 className="text-xl font-semibold text-white mb-2">{guru.name}</h3>
              <p className="text-white/80">{guru.description}</p>
            </div>
          ))}
        </div>

        {selectedGuru && (
          <div className="space-y-4 animate-fade-in">
            <h3 className="text-xl font-semibold text-white">
              Ask {gurus.find(g => g.id === selectedGuru)?.name}:
            </h3>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Enter your spiritual question here..."
              className="w-full h-32 p-4 rounded-xl bg-white/20 border border-white/30 text-white placeholder-white/60 resize-none focus:outline-none focus:ring-2 focus:ring-yellow-400"
            />
            <button
              onClick={askSpiritual}
              disabled={isLoading}
              className="bg-gradient-to-r from-pink-500 to-cyan-500 text-white px-8 py-3 rounded-full font-bold text-lg hover:scale-105 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Getting Guidance...' : 'Get Spiritual Guidance 🙏'}
            </button>
          </div>
        )}

        {(response || isLoading) && (
          <div className="mt-8 p-6 bg-white/20 rounded-xl animate-slide-up">
            {isLoading ? (
              <div className="text-center text-yellow-300">
                🧘‍♂️ The guru is contemplating your question...
              </div>
            ) : (
              <div className="space-y-4">
                <div className="border-b border-white/30 pb-4">
                  <strong className="text-yellow-300">
                    {gurus.find(g => g.id === selectedGuru)?.name} responds:
                  </strong>
                </div>
                <div className="text-white/90 leading-relaxed whitespace-pre-wrap">
                  {response}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default SpiritualGuidance;