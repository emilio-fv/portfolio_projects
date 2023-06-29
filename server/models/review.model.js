const mongoose = require('mongoose');
const { Schema } = mongoose;

const reviewSchema = new Schema({
  artist: {
    type: String,
    required: true,
  },
  artistId: {
    type: String,
    required: true
  },
  album: {
    type: String, 
    required: true
  },
  albumId: {
    type: String,
    required: true
  },
  src: {
    type: String,
    required: true
  }, 
  rating: {
    type: Number,
  },
  text: {
    type: String,
  },
  user: {
    type: Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  // likes: [{
  //   types: Schema.Types.ObjectId,
  //   ref: 'User'
  // }],
  // comments: [{
  //   types: Schema.Types.ObjectId,
  //   ref: 'Comment'
  // }]
}, { timestamps: true, collection: 'reviews' });

const Review = mongoose.model("Review", reviewSchema);

module.exports = {
  Review: Review
};