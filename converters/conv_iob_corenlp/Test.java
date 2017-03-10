package nlpTest;

import java.io.IOException;
import java.util.Iterator;
import java.util.List;

import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.sequences.CoNLLDocumentReaderAndWriter;
import edu.stanford.nlp.sequences.SeqClassifierFlags;
import edu.stanford.nlp.io.IOUtils;

public class Test {

	// http://stackoverflow.com/questions/31685738/named-entity-recognition-iob-annotation-transformation
	public static Iterator<List<CoreLabel>> loadCoNLLDocuments(String filePath, String outLabel) throws IOException{
	    SeqClassifierFlags inputFlags = new SeqClassifierFlags();
	    inputFlags.entitySubclassification = outLabel;//"noprefix";
	    inputFlags.retainEntitySubclassification = true;
	    CoNLLDocumentReaderAndWriter rw = new CoNLLDocumentReaderAndWriter();
	    rw.init(inputFlags);
	    Iterator<List<CoreLabel>> documents = rw.getIterator(IOUtils.readerFromString(filePath));
	    return documents;       
	}
	
	public static void main(String[] args) throws IOException, ClassNotFoundException {
	
		String outputLabel = null;
		String file = null;
		boolean skipWord = false, shen = false;
		
		if (args.length == 0){
			System.out.println("usage: -f <filename> -outlabel <destination label set> -skipWord -shen");
			return;
		}
		
		for ( int i=0; i<args.length; ++i ){
			if(args[i].equalsIgnoreCase("-f"))
				file = args[++i];
			else if(args[i].equalsIgnoreCase("-outlabel"))
				outputLabel = args[++i];
			else if (args[i].equalsIgnoreCase("-skipWord"))
				skipWord = true;
			else if (args[i].equalsIgnoreCase("-shen"))
					shen = true;
		}
		Iterator<List<CoreLabel>> itr = loadCoNLLDocuments(file, outputLabel);
		
		// The documents are List<CoreLabel>, token is a CoreLabel

		while(itr.hasNext()) {
			List<CoreLabel> list = itr.next();
			for (CoreLabel token : list){ 
//				String tokenTag = token.get(CoreAnnotations.AnswerAnnotation.class);
//				System.out.println(tokenTag);
				
				if (token.getString(CoreAnnotations.TextAnnotation.class).equals("*BOUNDARY*")){
					System.out.println();
					continue; //mondathatar
				}
				
				if (shen){
					
					//Shen formatum: pos, pos-iob
					System.out.println(token.getString(CoreAnnotations.PartOfSpeechAnnotation.class) + " " + 
							token.getString(CoreAnnotations.PartOfSpeechAnnotation.class) + "-" + token.getString(CoreAnnotations.AnswerAnnotation.class));
					
				}else{
					
					if (!skipWord)
						System.out.print(token.getString(CoreAnnotations.TextAnnotation.class) + " ");
					System.out.println(token.getString(CoreAnnotations.PartOfSpeechAnnotation.class) + " " + 
							token.getString(CoreAnnotations.AnswerAnnotation.class));
				}
			}
		}
		System.out.println();
	}
}
