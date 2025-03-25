prompt_template_outer = lambda e1, e2, e3, txt: f"""
### Annotation Instructions:
You are tasked with annotating a provided text for various opinion components. Follow the field descriptions and format guidelines to accurately capture the opinion information within the text.
{e1}
{e2}
{e3}
Follow the field descriptions and format guidelines to accurately annotate the opinions expressed within the input text.

**Input Text**: {txt}

**Annotated Output**:
"""
description_fields = """### Description of Opinion Fields:
1. **Sentiment Intensity**: It expresses the strength of the identified sentiment in an opinion. For the purpose of this work, we use ordinal values for sentiment intensity i.e. weak$<$average$<$strong.
an opinion. The value of sentiment intensity should never be N/A.
2. **Sentiment Polarity**: It is a predefined semantic orientation of the sentiment expressed in an opinion. It takes on one of the three polarity values i.e. postive, negative or neutral. The sentiment polarity cannot be N/A.
3. **Sentiment Expression**: The sentiment expression is the subjective statement (on an aspect) which indicates a presence of sentiment. It can be a word or a phrase explicitly present in the text. 
4. **Aspect Category**: Aspect Category of an entity represents a unique aspect of the entity. It expresses attributes or properties of the aforementioned entities.
5. **Aspect Term**: It is an expression i.e. actual word or phrases in the text indicating an aspect category. Like sentiment expression it must be explicitly present in the input text.
6. **Target Entity**: An entity is a product, service, topic, issue, person, organization, or event. The opinion is expressed with opinion expressions on the opinion target which are implicitly an aspect (or attribute) of the entity. 
7. **Opinion Holder Span **: An opinion holder (also called opinion source) is a person or organization who expressed an opinion. It must be explictly present in the input text.
7. **Opinion Holder Entity **: An entity is a product, service, topic, issue, person, organization, or event. Holder entities are the entity that is expressing the opinion.
8. **Opinion Qualifier**: A qualifier of an opinion limits or modifies the meaning of the opinion
9. **Opinion Reason**: A reason for an opinion is the cause of the opinion.
"""

format_guidelines = """### Format Guidelines:
1. Each opinion must be numbered and be annotated in the following template for generating opinion fields:
	- Opinion N
		- aspect_term:
		- sentiment_expression:
		- target_entity:
		- aspect_category:
		- sentiment_polarity:
		- sentiment_intensity:
		- opinion_holder_span:
		- opinion_holder_entity:
		- opinion_qualifier:
		- opinion_reason:
2. Only generate opinions where sentiment_polarity and sentiment_intensity are not N/A.
3. The generation should end once all the opinions are annotated.
"""
examples = """### Example 1:

**Input Text**: It 's a must read for anyone with an interest in cancer , professional or personal .

**Annotated Output**:
- Opinion 1
	- aspect_term: N/A
	- sentiment_expression: must read
	- target_entity: book
	- aspect_category: general
	- sentiment_polarity: positive
	- sentiment_intensity: strong
	- opinion_holder_span: N/A
	- opinion_holder_entity: author
	- opinion_qualifier: anyone with an interest in cancer , professional or personal
	- opinion_reason: N/A

### Example 2:

**Input Text**: I became fascinated with Robin Hobb 's writing only six months ago when I was introduced to her fantasy series .

**Annotated Output**:
- Opinion 1
	- aspect_term: robin hobb 's writing
	- sentiment_expression: N/A
	- target_entity: content
	- aspect_category: genre
	- sentiment_polarity: positive
	- sentiment_intensity: strong
	- opinion_holder_span: i
	- opinion_holder_entity: author
	- opinion_qualifier: N/A
	- opinion_reason: N/A

### Example 3:

**Input Text**: the screen looks great ( though maybe not if all you do is look at 4k resolution ) and the keyboard response feels pretty good .

**Annotated Output**:
- Opinion 1
	- aspect_term: screen
	- sentiment_expression: great
	- target_entity: display
	- aspect_category: operational_performance
	- sentiment_polarity: positive
	- sentiment_intensity: weak
	- opinion_holder_span: N/A
	- opinion_holder_entity: author
	- opinion_qualifier: N/A
	- opinion_reason: looks great ( though maybe not if all you do is look at 4k resolution )

- Opinion 2
	- aspect_term: keyboard response
	- sentiment_expression: pretty good
	- target_entity: keyboard
	- aspect_category: operational_performance
	- sentiment_polarity: positive
	- sentiment_intensity: average
	- opinion_holder_span: N/A
	- opinion_holder_entity: author
	- opinion_qualifier: N/A
	- opinion_reason: N/A
"""

prompt_template = lambda e1, e2, e3: lambda txt: prompt_template_outer(e1, e2, e3, txt)