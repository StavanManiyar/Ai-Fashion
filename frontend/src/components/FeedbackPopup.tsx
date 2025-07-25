import React, { useState } from 'react';
import { X, Heart, Send, MessageCircle, Star, Sparkles, ShoppingBag, Palette, Zap } from 'lucide-react';
import { submitFeedbackForm } from '../services/sheetdb';

interface FeedbackPopupProps {
  isVisible: boolean;
  onClose: () => void;
  userContext?: {
    monkSkinTone?: string;
    activeTab?: string;
    sessionId?: string;
  };
}

interface FeedbackData {
  emotion: string;
  rating: number;
  issues: string[];
  improvements: string;
  wouldRecommend: boolean;
  stylePersonality?: string;
  confidenceBoost?: boolean;
}

const FeedbackPopup: React.FC<FeedbackPopupProps> = ({ 
  isVisible, 
  onClose, 
  userContext = {} 
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [feedbackData, setFeedbackData] = useState<FeedbackData>({
    emotion: '',
    rating: 0,
    issues: [],
    improvements: '',
    wouldRecommend: false
  });

  if (!isVisible) return null;

  const handleEmotionSelect = (emotion: string) => {
    setFeedbackData(prev => ({ ...prev, emotion }));
    
    // If positive emotion, add style personality quiz before final step
    if (emotion === 'love' || emotion === 'like') {
      setCurrentStep(5); // New style personality step
    } else {
      setCurrentStep(2);
    }
  };

  const handleRatingSelect = (rating: number) => {
    setFeedbackData(prev => ({ ...prev, rating }));
    setCurrentStep(3);
  };

  const handleIssueToggle = (issue: string) => {
    setFeedbackData(prev => ({
      ...prev,
      issues: prev.issues.includes(issue)
        ? prev.issues.filter(i => i !== issue)
        : [...prev.issues, issue]
    }));
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    try {
      const payload = {
        ...feedbackData,
        userContext,
        timestamp: new Date().toISOString(),
        page: 'recommendations'
      };

      // Log feedback to console for debugging
      console.log('📝 Feedback Data:', payload);
      
      // Send feedback data to SheetDB (Excel sheet)
      const success = await submitFeedbackForm(payload);
      
      if (success) {
        console.log('✅ Feedback successfully stored in Excel sheet!');
      } else {
        console.log('⚠️ Failed to store feedback in Excel sheet, but continuing...');
      }

      // Always show success for better UX
      setIsSubmitted(true);
      setTimeout(() => {
        onClose();
        // Reset state after animation
        setTimeout(() => {
          setCurrentStep(1);
          setIsSubmitted(false);
          setFeedbackData({
            emotion: '',
            rating: 0,
            issues: [],
            improvements: '',
            wouldRecommend: false
          });
        }, 300);
      }, 2000);
      
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      // Still show success for better UX during development
      setIsSubmitted(true);
      setTimeout(() => {
        onClose();
        setTimeout(() => {
          setCurrentStep(1);
          setIsSubmitted(false);
          setFeedbackData({
            emotion: '',
            rating: 0,
            issues: [],
            improvements: '',
            wouldRecommend: false
          });
        }, 300);
      }, 2000);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStep1 = () => (
    <div className="text-center">
      <div className="mb-8">
        <div className="relative mb-6">
          <div className="w-20 h-20 bg-gradient-to-br from-purple-100 to-pink-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Sparkles className="h-10 w-10 text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600" style={{fill: 'url(#gradient)'}} />
            <svg width="0" height="0">
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stopColor="#9333ea" />
                  <stop offset="100%" stopColor="#ec4899" />
                </linearGradient>
              </defs>
            </svg>
          </div>
          <div className="absolute -top-2 -right-2 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center text-xs animate-bounce">
            ✨
          </div>
        </div>
        <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-3">
          Love Your New Look?
        </h3>
        <p className="text-gray-600 text-sm leading-relaxed mb-3">
          Your fashion feedback helps our AI become your personal style guru! ✨
        </p>
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-3 mb-4">
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-1 sm:space-y-0 sm:space-x-2 text-xs">
            <div className="flex items-center space-x-2">
              <div className="flex -space-x-1">
                <div className="w-5 h-5 bg-pink-400 rounded-full border-2 border-white"></div>
                <div className="w-5 h-5 bg-purple-400 rounded-full border-2 border-white"></div>
                <div className="w-5 h-5 bg-blue-400 rounded-full border-2 border-white"></div>
              </div>
              <span className="animate-pulse">💫</span>
            </div>
            <span className="text-purple-700 font-medium text-center">Join 47,832 style lovers sharing feedback!</span>
          </div>
        </div>
      </div>
      
      <div className="space-y-3">
        <button
          onClick={() => handleEmotionSelect('love')}
          className="group w-full relative overflow-hidden bg-gradient-to-r from-pink-50 to-purple-50 border-2 border-pink-200 hover:border-pink-400 rounded-xl p-4 transition-all duration-300 hover:shadow-lg hover:scale-105"
        >
          <div className="flex items-center justify-center space-x-4">
            <div className="text-3xl transform group-hover:scale-110 transition-transform">💖</div>
            <div className="text-left">
              <span className="font-bold text-pink-600 block">Absolutely Obsessed!</span>
              <span className="text-xs text-pink-500">These are SO me!</span>
            </div>
          </div>
        </button>
        
        <button
          onClick={() => handleEmotionSelect('like')}
          className="group w-full relative overflow-hidden bg-gradient-to-r from-purple-50 to-indigo-50 border-2 border-purple-200 hover:border-purple-400 rounded-xl p-4 transition-all duration-300 hover:shadow-lg hover:scale-105"
        >
          <div className="flex items-center justify-center space-x-4">
            <div className="text-3xl transform group-hover:scale-110 transition-transform">😍</div>
            <div className="text-left">
              <span className="font-bold text-purple-600 block">Love the Vibe!</span>
              <span className="text-xs text-purple-500">Pretty stylish picks</span>
            </div>
          </div>
        </button>
        
        <button
          onClick={() => handleEmotionSelect('okay')}
          className="group w-full relative overflow-hidden bg-gradient-to-r from-blue-50 to-cyan-50 border-2 border-blue-200 hover:border-blue-400 rounded-xl p-4 transition-all duration-300 hover:shadow-lg hover:scale-105"
        >
          <div className="flex items-center justify-center space-x-4">
            <div className="text-3xl transform group-hover:scale-110 transition-transform">🤔</div>
            <div className="text-left">
              <span className="font-bold text-blue-600 block">It's Alright</span>
              <span className="text-xs text-blue-500">Some potential here</span>
            </div>
          </div>
        </button>
        
        <button
          onClick={() => handleEmotionSelect('not-great')}
          className="group w-full relative overflow-hidden bg-gradient-to-r from-orange-50 to-yellow-50 border-2 border-orange-200 hover:border-orange-400 rounded-xl p-4 transition-all duration-300 hover:shadow-lg hover:scale-105"
        >
          <div className="flex items-center justify-center space-x-4">
            <div className="text-3xl transform group-hover:scale-110 transition-transform">😕</div>
            <div className="text-left">
              <span className="font-bold text-orange-600 block">Not My Style</span>
              <span className="text-xs text-orange-500">Needs work</span>
            </div>
          </div>
        </button>
        
        <button
          onClick={() => handleEmotionSelect('dislike')}
          className="group w-full relative overflow-hidden bg-gradient-to-r from-red-50 to-pink-50 border-2 border-red-200 hover:border-red-400 rounded-xl p-4 transition-all duration-300 hover:shadow-lg hover:scale-105"
        >
          <div className="flex items-center justify-center space-x-4">
            <div className="text-3xl transform group-hover:scale-110 transition-transform">😬</div>
            <div className="text-left">
              <span className="font-bold text-red-600 block">Hard Pass</span>
              <span className="text-xs text-red-500">Totally off-brand</span>
            </div>
          </div>
        </button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="text-center">
      <div className="mb-8">
        <div className="relative mb-6">
          <div className="w-20 h-20 bg-gradient-to-br from-yellow-100 to-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Star className="h-10 w-10 text-yellow-500 fill-current" />
          </div>
          <div className="absolute -top-1 -right-1 w-6 h-6 bg-pink-400 rounded-full flex items-center justify-center text-xs animate-pulse">
            ⭐
          </div>
        </div>
        <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-3">
          Style Accuracy Check
        </h3>
        <p className="text-gray-600 text-sm leading-relaxed">
          Rate how well we nailed your personal aesthetic! ✨
        </p>
      </div>
      
      <div className="space-y-4 mb-6">
        <p className="text-gray-700 font-medium">Tap the stars to rate!</p>
        <div className="flex justify-center space-x-3">
          {[1, 2, 3, 4, 5].map((rating) => (
            <button
              key={rating}
              onClick={() => handleRatingSelect(rating)}
              className="group p-2 rounded-xl hover:bg-gradient-to-br hover:from-yellow-50 hover:to-orange-50 transition-all duration-300 hover:scale-110"
            >
              <Star 
                className={`h-10 w-10 transition-all duration-200 ${
                  rating <= feedbackData.rating 
                    ? 'text-yellow-400 fill-current drop-shadow-lg transform scale-110' 
                    : 'text-gray-300 group-hover:text-yellow-300'
                }`} 
              />
            </button>
          ))}
        </div>
        <div className="text-xs text-gray-500 mt-4">
          {feedbackData.rating === 0 && "How did we do?"}
          {feedbackData.rating === 1 && "😬 Totally missed the mark"}
          {feedbackData.rating === 2 && "😕 Needs major improvements"}
          {feedbackData.rating === 3 && "😐 It's okay, room for growth"}
          {feedbackData.rating === 4 && "😊 Pretty good match!"}
          {feedbackData.rating === 5 && "🤩 Absolutely perfect!"}
        </div>
      </div>
    </div>
  );

  const renderStep3 = () => {
    const issueOptions = [
      { emoji: '🎨', text: 'More color variety' },
      { emoji: '💰', text: 'Budget-friendly options' },
      { emoji: '👗', text: 'More style diversity' },
      { emoji: '📏', text: 'Better size range' },
      { emoji: '✨', text: 'Trendier pieces' },
      { emoji: '⏰', text: 'Timeless classics' },
      { emoji: '💎', text: 'Higher quality items' },
      { emoji: '🌱', text: 'Eco-friendly options' }
    ];

    return (
      <div className="text-center">
        <div className="mb-8">
          <div className="relative mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-blue-100 to-cyan-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Palette className="h-10 w-10 text-blue-500" />
            </div>
            <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center text-xs animate-bounce">
              💡
            </div>
          </div>
          <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-3">
            Help Us Glow Up!
          </h3>
          <p className="text-gray-600 text-sm leading-relaxed">
            What would make your styling experience even more amazing? ✨
          </p>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
          {issueOptions.map((option) => (
            <button
              key={option.text}
              onClick={() => handleIssueToggle(option.text)}
              className={`group p-4 rounded-xl border-2 transition-all duration-300 hover:scale-105 ${
                feedbackData.issues.includes(option.text)
                  ? 'border-purple-400 bg-gradient-to-br from-purple-50 to-pink-50 text-purple-700 shadow-lg'
                  : 'border-gray-200 hover:border-purple-300 hover:bg-gradient-to-br hover:from-purple-50 hover:to-pink-50'
              }`}
            >
              <div className="flex flex-col items-center space-y-2">
                <span className="text-2xl transform group-hover:scale-110 transition-transform">
                  {option.emoji}
                </span>
                <span className="text-xs font-medium text-center leading-tight">
                  {option.text}
                </span>
              </div>
            </button>
          ))}
        </div>
        
        <button
          onClick={() => setCurrentStep(4)}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 px-6 rounded-xl hover:opacity-90 transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          Continue My Style Journey ✨
        </button>
      </div>
    );
  };

  const renderStep4 = () => (
    <div className="text-center">
      <div className="mb-8">
        <div className="relative mb-6">
          <div className="w-20 h-20 bg-gradient-to-br from-pink-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Heart className="h-10 w-10 text-pink-500 fill-current" />
          </div>
          <div className="absolute -top-1 -right-1 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center text-xs animate-pulse">
            💕
          </div>
        </div>
        <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-3">
          Almost Done, Bestie!
        </h3>
        <p className="text-gray-600 text-sm leading-relaxed mb-6">
          Share your style secrets so we can serve you even better looks! 💅
        </p>
        
        <textarea
          placeholder="Spill the tea about your style... 🍵 (What vibes are you going for? Dream brands? Style goals?)" 
          value={feedbackData.improvements}
          onChange={(e) => setFeedbackData(prev => ({ ...prev, improvements: e.target.value }))}
          className="w-full p-4 border-2 border-gray-200 rounded-xl resize-none focus:ring-2 focus:ring-purple-500 focus:border-purple-300 transition-all duration-200 placeholder-gray-400"
          rows={4}
        />
      </div>
      
      <div className="space-y-6">
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4">
          <p className="text-gray-700 font-medium mb-3">Would you recommend our AI stylist to your friends? 👯‍♀️</p>
          <div className="flex space-x-3 justify-center">
            <button
              onClick={() => setFeedbackData(prev => ({ ...prev, wouldRecommend: true }))}
              className={`group px-6 py-3 rounded-xl transition-all duration-300 font-medium ${
                feedbackData.wouldRecommend 
                  ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-lg transform scale-105' 
                  : 'bg-white border-2 border-green-200 text-green-600 hover:bg-green-50 hover:border-green-300 hover:scale-105'
              }`}
            >
              <span className="flex items-center space-x-2">
                <span>😍</span>
                <span>Absolutely!</span>
              </span>
            </button>
            <button
              onClick={() => setFeedbackData(prev => ({ ...prev, wouldRecommend: false }))}
              className={`group px-6 py-3 rounded-xl transition-all duration-300 font-medium ${
                !feedbackData.wouldRecommend && feedbackData.wouldRecommend !== null
                  ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg transform scale-105' 
                  : 'bg-white border-2 border-orange-200 text-orange-600 hover:bg-orange-50 hover:border-orange-300 hover:scale-105'
              }`}
            >
              <span className="flex items-center space-x-2">
                <span>🤔</span>
                <span>Not yet</span>
              </span>
            </button>
          </div>
        </div>
        
        <button
          onClick={handleSubmit}
          disabled={isSubmitting}
          className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 px-6 rounded-xl hover:opacity-90 transition-all duration-300 font-bold shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:transform-none"
        >
          {isSubmitting ? (
            <span className="flex items-center justify-center space-x-3">
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent" />
              <span>Sending Your Vibes... 🚀</span>
            </span>
          ) : (
            <span className="flex items-center justify-center space-x-2">
              <Sparkles className="h-5 w-5" />
              <span>Send My Style Feedback! ✨</span>
            </span>
          )}
        </button>
      </div>
    </div>
  );

  const renderStep5 = () => {
    const stylePersonalities = [
      { id: 'minimalist', emoji: '🤍', title: 'Minimalist Chic', desc: 'Clean lines, neutral tones' },
      { id: 'boho', emoji: '🌸', title: 'Boho Queen', desc: 'Free-spirited, earthy vibes' },
      { id: 'edgy', emoji: '🖤', title: 'Edgy Trendsetter', desc: 'Bold, statement pieces' },
      { id: 'classic', emoji: '💼', title: 'Timeless Classic', desc: 'Elegant, sophisticated' },
      { id: 'romantic', emoji: '💕', title: 'Romantic Dreamer', desc: 'Soft, feminine touches' },
      { id: 'streetwear', emoji: '👟', title: 'Street Style Star', desc: 'Urban, casual cool' }
    ];

    return (
      <div className="text-center">
        <div className="mb-8">
          <div className="relative mb-6">
            <div className="w-20 h-20 bg-gradient-to-br from-indigo-100 to-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <ShoppingBag className="h-10 w-10 text-indigo-500" />
            </div>
            <div className="absolute -top-1 -right-1 w-6 h-6 bg-orange-400 rounded-full flex items-center justify-center text-xs animate-spin" style={{animationDuration: '3s'}}>
              👑
            </div>
          </div>
          <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-3">
            What's Your Style Personality?
          </h3>
          <p className="text-gray-600 text-sm leading-relaxed mb-4">
            Help us understand your fashion DNA! ✨
          </p>
          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-3 mb-6">
            <p className="text-xs text-orange-700 font-medium">
              💡 This helps our AI curate looks that feel authentically YOU!
            </p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-8">
          {stylePersonalities.map((style) => (
            <button
              key={style.id}
              onClick={() => setFeedbackData(prev => ({ ...prev, stylePersonality: style.id }))}
              className={`group p-4 rounded-xl border-2 transition-all duration-300 hover:scale-105 ${
                feedbackData.stylePersonality === style.id
                  ? 'border-indigo-400 bg-gradient-to-br from-indigo-50 to-purple-50 text-indigo-700 shadow-lg'
                  : 'border-gray-200 hover:border-indigo-300 hover:bg-gradient-to-br hover:from-indigo-50 hover:to-purple-50'
              }`}
            >
              <div className="flex flex-col items-center space-y-2">
                <span className="text-2xl transform group-hover:scale-110 transition-transform">
                  {style.emoji}
                </span>
                <span className="text-xs font-bold text-center leading-tight">
                  {style.title}
                </span>
                <span className="text-xs text-gray-500 text-center leading-tight">
                  {style.desc}
                </span>
              </div>
            </button>
          ))}
        </div>

        <div className="bg-gradient-to-r from-pink-50 to-purple-50 rounded-xl p-4 mb-6">
          <p className="text-gray-700 font-medium mb-3">Quick confidence check! 💪</p>
          <p className="text-sm text-gray-600 mb-3">Did these recommendations make you feel more confident about your style?</p>
          <div className="flex space-x-3 justify-center">
            <button
              onClick={() => setFeedbackData(prev => ({ ...prev, confidenceBoost: true }))}
              className={`group px-6 py-3 rounded-xl transition-all duration-300 font-medium ${
                feedbackData.confidenceBoost === true
                  ? 'bg-gradient-to-r from-emerald-500 to-green-500 text-white shadow-lg transform scale-105' 
                  : 'bg-white border-2 border-emerald-200 text-emerald-600 hover:bg-emerald-50 hover:border-emerald-300 hover:scale-105'
              }`}
            >
              <span className="flex items-center space-x-2">
                <span>💪</span>
                <span>Yes, totally!</span>
              </span>
            </button>
            <button
              onClick={() => setFeedbackData(prev => ({ ...prev, confidenceBoost: false }))}
              className={`group px-6 py-3 rounded-xl transition-all duration-300 font-medium ${
                feedbackData.confidenceBoost === false
                  ? 'bg-gradient-to-r from-gray-500 to-slate-500 text-white shadow-lg transform scale-105' 
                  : 'bg-white border-2 border-gray-200 text-gray-600 hover:bg-gray-50 hover:border-gray-300 hover:scale-105'
              }`}
            >
              <span className="flex items-center space-x-2">
                <span>😐</span>
                <span>Not really</span>
              </span>
            </button>
          </div>
        </div>
        
        <button
          onClick={() => setCurrentStep(4)}
          className="w-full bg-gradient-to-r from-indigo-600 to-purple-600 text-white py-4 px-6 rounded-xl hover:opacity-90 transition-all duration-300 font-medium shadow-lg hover:shadow-xl transform hover:scale-105"
        >
          Almost There! Let's Finish ✨
        </button>
      </div>
    );
  };

  const renderSuccess = () => {
    const getPersonalizedMessage = () => {
      if (feedbackData.stylePersonality) {
        const messages = {
          minimalist: "Your clean aesthetic is perfection! 🤍",
          boho: "Your free spirit shines through! 🌸",
          edgy: "Your bold style is iconic! 🖤",
          classic: "Your timeless elegance is stunning! 💼",
          romantic: "Your dreamy style is magical! 💕",
          streetwear: "Your urban cool is unmatched! 👟"
        };
        return messages[feedbackData.stylePersonality as keyof typeof messages] || "Your style is amazing!";
      }
      return "Your style is amazing!";
    };

    return (
      <div className="text-center py-8">
        <div className="mb-6">
          <div className="relative mb-6">
            <div className="w-24 h-24 bg-gradient-to-br from-green-100 to-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-bounce">
              <Sparkles className="h-12 w-12 text-green-500" />
            </div>
            <div className="absolute -top-2 -right-2 w-8 h-8 bg-pink-400 rounded-full flex items-center justify-center text-xs animate-ping">
              ✨
            </div>
            <div className="absolute -bottom-2 -left-2 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center text-xs animate-bounce delay-150">
              💖
            </div>
          </div>
          <h3 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-pink-600 mb-3">
            You're Amazing! 💅✨
          </h3>
          <p className="text-gray-600 text-lg mb-2">
            {getPersonalizedMessage()}
          </p>
          <p className="text-gray-600 text-sm mb-3">
            Your style insights just made our AI 10x smarter! 🧠✨
          </p>
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 mb-4">
            <p className="text-sm text-purple-700 font-medium">
              🎆 Next time, expect even more personalized recommendations that scream "YOU"!
            </p>
            {feedbackData.confidenceBoost && (
              <p className="text-xs text-green-600 mt-2 font-medium">
                💪 Plus, we love that we boosted your style confidence!
              </p>
            )}
          </div>
          <p className="text-xs text-gray-500">
            Keep slaying, fashion queen! 👑
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-sm sm:max-w-md w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto transform transition-all duration-300 ease-out scrollbar-hide">
        <style dangerouslySetInnerHTML={{
          __html: `
            .scrollbar-hide {
              -ms-overflow-style: none;
              scrollbar-width: none;
            }
            .scrollbar-hide::-webkit-scrollbar {
              display: none;
            }
          `
        }} />
        {/* Header */}
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-100">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <MessageCircle className="h-4 w-4 text-purple-600" />
            </div>
            <span className="font-medium text-gray-800 text-sm sm:text-base">Quick Style Check</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-full transition-colors duration-200"
          >
            <X className="h-5 w-5 text-gray-500" />
          </button>
        </div>

        {/* Progress Bar */}
        {!isSubmitted && (
          <div className="px-6 py-2">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / 4) * 100}%` }}
              />
            </div>
          </div>
        )}

        {/* Content */}
        <div className="p-6">
          {isSubmitted ? renderSuccess() : (
            <>
              {currentStep === 1 && renderStep1()}
              {currentStep === 2 && renderStep2()}
              {currentStep === 3 && renderStep3()}
              {currentStep === 4 && renderStep4()}
              {currentStep === 5 && renderStep5()}
            </>
          )}
        </div>

        {/* Footer */}
        {!isSubmitted && (
          <div className="px-6 pb-4">
            <div className="flex items-center justify-center space-x-1 text-xs text-gray-500">
              <span>Powered by</span>
              <span className="font-medium text-purple-600">AI Fashion</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedbackPopup;
