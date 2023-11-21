from inspect import getargs, isclass, signature


class Builder:
    def __make_func(prop):
        def func(s2, val):
            setattr(s2, prop, val)
            return s2
        return func

    def __call__(self, decorated_class):
        props = getargs(decorated_class.__init__.__code__).args[1:]
        class InnerBuilder:
            def build(s2) -> decorated_class:
                return decorated_class(*(getattr(s2, prop) for prop in props))  
              
        for prop in props:
            func = Builder.__make_func(prop)
            setattr(InnerBuilder, f'set_{prop}', func)
        
        decorated_class.Builder = InnerBuilder
        return decorated_class
    
x = int
print(isclass(x))

print(*signature(Builder.__init__).parameters.items())