prompt_template_part = lambda txt, format_name, uoc_exp:f"""
### Annotation Instructions:
You are tasked with annotating a provided text for various opinion components. Follow the ontological descriptions and format guidelines to accurately capture the opinion information within the text.

### {format_name} description of opinion:
```
{uoc_exp}
```
### Format Guidelines:
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

Use the format guidelines and examples provided to annotate opinions in the given input text.
### Example 1:

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

Follow the ontology description and format guidelines to accurately annotate the opinions expressed within the input text.
**Input Text**: {txt}

**Annotated Output**:
"""

prompt_template = lambda uoc_exp, format_name: lambda txt: prompt_template_part(txt, format_name, uoc_exp)