import React from 'react';

const SentimentCard = ({ company, sentiment, onClick }) => {
  return (
    <div className="sentiment-card" onClick={() => onClick(company)}>
      <h3>{company}</h3>
      <p>{sentiment}</p>
    </div>
  );
}

export default SentimentCard;
