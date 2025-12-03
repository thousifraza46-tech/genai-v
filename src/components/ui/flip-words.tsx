import React from "react";

export const FlipWords = ({
  words,
  className,
}: {
  words: string[];
  className?: string;
}) => {
  return (
    <div className={`relative inline-block ${className}`}>
      <div className="relative h-[1.2em] overflow-hidden">
        <div className="animate-flip-words">
          {words.map((word, index) => (
            <div
              key={index}
              className="absolute w-full text-center"
              style={{
                top: `${index * 100}%`,
              }}
            >
              {word}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
