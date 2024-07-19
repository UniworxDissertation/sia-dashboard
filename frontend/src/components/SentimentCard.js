import React from 'react';

const SentimentCard = ({ company, sentiment }) => {
  return (
    <div className="sentiment-card">
      <h3>{company}</h3>
      <p>{sentiment}</p>
    </div>
  );
}

export default SentimentCard;