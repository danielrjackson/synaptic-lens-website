export function confidenceSummary(original,replacement,truths) {
 const mean=xs=>xs.reduce((a,b)=>a+b,0)/xs.length;
 let higher=0,lower=0,same=0,broken=0,brokenHigher=0,stillWrong=0;
 truths.forEach((truth,i)=>{const delta=replacement.correct_probability[i]-original.correct_probability[i];if(delta>1e-9)higher++;else if(delta< -1e-9)lower++;else same++;
 if(original.answers[i]===truth&&replacement.answers[i]!==truth){broken++;if(delta>1e-9)brokenHigher++;}
 if(replacement.answers[i]!==truth)stillWrong++;
 });
 return {meanProbability:mean(replacement.correct_probability),meanNll:mean(replacement.nll),higher,lower,same,broken,brokenHigher,wrong:stillWrong};
}
