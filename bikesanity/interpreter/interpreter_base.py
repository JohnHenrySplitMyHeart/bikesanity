
class InterpreterBase:

    def remove_everything_before(self, tag, including=False):
        for sibling in tag.find_previous_siblings():
            sibling.decompose()
        if including: tag.decompose()

    def find_body_ancestor(self, tag):
        if not tag.parent:
            return None, None
        elif tag.parent.name == 'body':
            return tag, tag.parent
        else:
            return self.find_body_ancestor(tag.parent)

    def remove_everything_before_body_level(self, tag, including=False):
        # Find the ancestor element that has body as a parent
        body_parent, body = self.find_body_ancestor(tag)
        if body_parent:
            self.remove_everything_before(body_parent, including)
            return body

    def replace_invalid_tag(self, doc, tag):
        for match in doc.findAll(tag):
            match.unwrap()
